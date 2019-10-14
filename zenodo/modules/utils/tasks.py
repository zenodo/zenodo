# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Celery tasks for Zenodo utility functions."""

from __future__ import absolute_import, unicode_literals

from collections import namedtuple
from datetime import datetime
from itertools import chain as ichain

import sqlalchemy as sa
from celery import chain, group, shared_task
from celery.utils.log import get_task_logger
from dictdiffer import diff
from elasticsearch_dsl import Q
from flask import current_app
from flask_mail import Message
from invenio_db import db
from invenio_files_rest.models import FileInstance
from invenio_indexer.api import RecordIndexer
from invenio_oaiserver.minters import oaiid_minter
from invenio_oaiserver.models import OAISet
from invenio_oaiserver.query import OAIServerSearch
from invenio_oaiserver.utils import datetime_to_datestamp
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_records_files.models import RecordsBuckets
from six.moves import filter

from zenodo.modules.records.serializers.schemas.common import ui_link_for
from zenodo.modules.records.utils import is_deposit, is_record

logger = get_task_logger(__name__)

#
# OAI Syncing task
#
# Cache object for fetched OAISets
OAISetCache = namedtuple('OAISetCache', ('search_pattern', ))


def update_oaisets_cache(cache, data):
    """Update the OAISet cache with OAISets from data."""
    specs = data.get('_oai', {}).get('sets', [])
    for spec in specs:
        if spec not in cache:
            q = OAISet.query.filter_by(spec=spec)
            if q.count():
                cache[spec] = OAISetCache(
                    search_pattern=q.one().search_pattern)


def resolve_oaiset(spec, cache=None):
    """Resolve OAISet from spec with cache support."""
    if cache is not None and spec in cache:
        return cache[spec]
    else:
        oaiset = OAISet.query.filter_by(spec=spec).one()
        if cache is not None:
            cache[spec] = OAISetCache(search_pattern=oaiset.search_pattern)
        return oaiset


def get_synced_sets(record, cache=None):
    """Get the synced OAI set list."""
    comms = record.get('communities', [])
    sets = record.get('_oai', {}).get('sets', [])
    other_sets = [s for s in sets if not (s.startswith('user-') and
                  not resolve_oaiset(s, cache=cache).search_pattern)]
    s_comms = ['user-{0}'.format(c) for c in comms]
    return sorted(other_sets + s_comms)


def comm_sets_match(record, cache=None):
    """Check if communities definition and OAI sets match."""
    # OAI sets of communities
    comms = record.get('communities', [])
    s_comms = ['user-{0}'.format(c) for c in comms]

    # Community-based OAI sets
    sets = record.get('_oai', {}).get('sets', [])
    c_sets = [s for s in sets if s.startswith('user-') and
              not resolve_oaiset(s, cache=cache).search_pattern]
    return set(c_sets) == set(s_comms)


def requires_sync(record, cache=None):
    """Determine whether record requries OAI information syncinc."""
    oai = record.get('_oai', {})
    return (not oai.get('id')) or (oai.get('updated') is None) or \
        (not comm_sets_match(record, cache=cache))


@shared_task
def sync_record_oai(uuid, cache=None):
    """Mint OAI ID information for the record.

    :type uuid: str
    """
    rec = Record.get_record(uuid)
    recid_s = str(rec['recid'])

    # Try to get the already existing OAI PID for this record
    oai_pid_q = PersistentIdentifier.query.filter_by(pid_type='oai',
                                                     object_uuid=rec.id)
    if oai_pid_q.count() == 0:
        pid = oaiid_minter(rec.id, rec)
        synced_sets = get_synced_sets(rec, cache=cache)
        rec['_oai']['sets'] = synced_sets
        rec.commit()
        db.session.commit()
        RecordIndexer().bulk_index([str(rec.id), ])
        logger.info('Minted new OAI PID ({pid}) for record {id}'.format(
            pid=pid, id=uuid))
    elif oai_pid_q.count() == 1:
        pid = oai_pid_q.one()
        managed_prefixes = current_app.config['OAISERVER_MANAGED_ID_PREFIXES']
        if not any(pid.pid_value.startswith(p) for p in managed_prefixes):
            logger.exception('Unknown OAIID prefix: {0}'.format(pid.pid_value))
        elif str(pid.get_assigned_object()) != uuid:
            logger.exception(
                'OAI PID ({pid}) for record {id} ({recid}) is '
                'pointing to a different object ({id2})'.format(
                    pid=pid, id=uuid, id2=str(pid.get_assigned_object()),
                    recid=recid_s))
        elif requires_sync(rec, cache=cache):
            rec.setdefault('_oai', {})
            rec['_oai']['id'] = pid.pid_value
            rec['_oai']['updated'] = datetime_to_datestamp(datetime.utcnow())
            synced_sets = get_synced_sets(rec, cache=cache)
            rec['_oai']['sets'] = synced_sets
            if not rec['_oai']['sets']:
                del rec['_oai']['sets']  # Don't store empty list
            rec.commit()
            db.session.commit()
            RecordIndexer().bulk_index([str(rec.id), ])
            logger.info('Matching OAI PID ({pid}) for record {id}'.format(
                pid=pid, id=uuid))


#
# Files metadata repair task
#
def has_corrupted_files_meta(record):
    """Determine whether the metadata contains corrupted files information."""
    rb = record['_buckets']['record']
    return any(f['bucket'] != rb for f in record.get('_files', []))


def recent_non_corrupted_revision(record):
    """Get the most recent non-corrupted revision of a record."""
    return next(filter(lambda rev: not has_corrupted_files_meta(rev),
                       reversed(record.revisions)))


def files_diff_safe(files_diff):
    """Make sure there is no unsafe operation on files dictionaries."""
    # Mark diff as unsafe if there are any additions or removals of files
    if any(op[0] in ('add', 'remove') for op in files_diff):
        return False
    # Mark diff as unsafe if the changes include fields other than the
    # bucket or version_if
    changes = filter(lambda op: op[0] == 'change', files_diff)
    if any(op[1][1] not in ('bucket', 'version_id') for op in changes):
        return False
    return True


@shared_task
def repair_record_metadata(uuid):
    """Repair the record's metadata using a reference revision."""
    rec = Record.get_record(uuid)
    good_revision = recent_non_corrupted_revision(rec)
    if '_internal' in good_revision:
        rec['_internal'] = good_revision['_internal']
    files_diff = list(diff(rec['_files'], good_revision['_files']))
    if files_diff_safe(files_diff):
        rec['_files'] = good_revision['_files']
    rec.commit()
    db.session.commit()
    RecordIndexer().bulk_index([str(rec.id), ])


@shared_task
def remove_oaiset_spec(record_uuid, spec):
    """Remove the OAI spec from the record and commit."""
    rec = Record.get_record(record_uuid)
    rec['_oai']['sets'] = sorted(set([s for s in rec['_oai'].get('sets', [])
                                      if s != spec]))
    rec['_oai']['updated'] = datetime_to_datestamp(datetime.utcnow())
    if not rec['_oai']['sets']:
        del rec['_oai']['sets']
    rec.commit()
    db.session.commit()
    RecordIndexer().bulk_index([str(rec.id), ])


@shared_task
def add_oaiset_spec(record_uuid, spec):
    """Add the OAI spec to the record and commit."""
    rec = Record.get_record(record_uuid)
    rec['_oai']['sets'] = sorted(set(rec['_oai'].get('sets', []) + [spec, ]))
    rec['_oai']['updated'] = datetime_to_datestamp(datetime.utcnow())
    rec.commit()
    db.session.commit()
    RecordIndexer().bulk_index([str(rec.id), ])


def iter_record_oai_tasks(query, spec, func):
    """Turn an ES query and a task function into an iterable of celery tasks.

    :param query: Elasticsearch query
    :type query: elasticsearch_dsl.Q
    :param spec: OAISet.spec name
    :type spec: str
    :param func: shared_task function to execute for given record
    :type func: function
    """
    search = OAIServerSearch(
        index=current_app.config['OAISERVER_RECORD_INDEX'],
    ).query(query)
    for result in search.scan():
        yield func.si(result.meta.id, spec)


def make_oai_task_group(oais):
    """Make a celery group for an OAISet.

    Since for each OAISet any given record has to be modified by either
    removing or adding the OAISet.spec, it's save to create a single
    group per OAISet for all records (no risk of racing conditions in parallel
    execution).

    :param oais: OAISet for which the task group is to be made.
    :type oais: invenio_oaiserver.modules.OAISet
    """
    spec_q = Q('match', **{'_oai.sets': oais.spec})
    pattern_q = Q('query_string', query=oais.search_pattern)
    spec_remove_q = Q('bool', must=spec_q, must_not=pattern_q)
    spec_add_q = Q('bool', must=pattern_q, must_not=spec_q)
    return group(ichain(iter_record_oai_tasks(spec_remove_q, oais.spec,
                                              remove_oaiset_spec),
                        iter_record_oai_tasks(spec_add_q, oais.spec,
                                              add_oaiset_spec)))


@shared_task
def update_search_pattern_sets():
    """Update all records affected by search-patterned OAISets.

    In order to avoid racing condition when editing the records, all
    OAISet task groups are chained.
    """
    oaisets = OAISet.query.filter(OAISet.search_pattern.isnot(None))
    chain(make_oai_task_group(oais) for oais in oaisets).apply_async()


def format_file_integrity_report(report):
    """Format the email body for the file integrity report."""
    lines = []
    for entry in report:
        f = entry['file']
        lines.append('ID: {}'.format(str(f.id)))
        lines.append('URI: {}'.format(f.uri))
        lines.append('Name: {}'.format(entry.get('filename')))
        lines.append('Created: {}'.format(f.created))
        lines.append('Checksum: {}'.format(f.checksum))
        lines.append('Last Check: {}'.format(f.last_check_at))
        if 'record' in entry:
            lines.append(u'Record: {}'.format(
                ui_link_for('record_html', id=entry['record'].get('recid'))
            ))
        if 'deposit' in entry:
            lines.append(u'Deposit: {}'.format(
                ui_link_for(
                    'deposit_html',
                    id=entry['deposit'].get('_deposit', {}).get('id'))
            ))
        lines.append(('-' * 80) + '\n')
    return '\n'.join(lines)


@shared_task
def file_integrity_report():
    """Send a report of uhealthy/missing files to Zenodo admins."""
    # First retry verifying files that errored during their last check
    files = FileInstance.query.filter(FileInstance.last_check.is_(None))
    for f in files:
        try:
            f.clear_last_check()
            db.session.commit()
            f.verify_checksum(throws=False)
            db.session.commit()
        except Exception:
            pass  # Don't fail sending the report in case of some file error

    report = []
    unhealthy_files = (
        FileInstance.query
        .filter(sa.or_(FileInstance.last_check.is_(None),
                       FileInstance.last_check.is_(False)))
        .order_by(FileInstance.created.desc()))

    for f in unhealthy_files:
        entry = {'file': f}
        for o in f.objects:
            entry['filename'] = o.key
            # Find records/deposits for the files
            rb = RecordsBuckets.query.filter(
                RecordsBuckets.bucket_id == o.bucket_id).one_or_none()
            if rb and rb.record and rb.record.json:
                if is_deposit(rb.record.json):
                    entry['deposit'] = rb.record.json
                elif is_record(rb.record.json):
                    entry['record'] = rb.record.json
        report.append(entry)

    if report:
        # Format and send the email
        subject = u'Zenodo files integrity report [{}]'.format(datetime.now())
        body = format_file_integrity_report(report)
        sender = current_app.config['ZENODO_SYSTEM_SENDER_EMAIL']
        recipients = [current_app.config['ZENODO_ADMIN_EMAIL']]
        msg = Message(subject, sender=sender, recipients=recipients, body=body)
        current_app.extensions['mail'].send(msg)
