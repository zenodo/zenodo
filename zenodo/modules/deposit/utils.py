# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utilities for Zenodo deposit."""

from __future__ import absolute_import, unicode_literals

import itertools
import uuid

import pycountry
from elasticsearch.exceptions import NotFoundError
from flask import abort, current_app, request
from invenio_accounts.models import User
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.models import RecordsBuckets
from six import string_types, text_type
from werkzeug.local import LocalProxy
from werkzeug.routing import PathConverter

from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.deposit.tasks import datacite_inactivate, datacite_register
from zenodo.modules.openaire.helpers import openaire_datasource_id, \
    openaire_original_id, openaire_type
from zenodo.modules.openaire.tasks import openaire_delete
from zenodo.modules.records.api import ZenodoRecord


def file_id_to_key(value):
    """Convert file UUID to value if in request context."""
    from invenio_files_rest.models import ObjectVersion

    _, record = request.view_args['pid_value'].data
    if value in record.files:
        return value

    try:
        value = uuid.UUID(value)
    except ValueError:
        abort(404)

    object_version = ObjectVersion.query.filter_by(
        bucket_id=record.files.bucket.id, file_id=value
    ).first()
    if object_version:
        return object_version.key
    return value


class FileKeyConverter(PathConverter):
    """Convert file UUID for key."""

    def to_python(self, value):
        """Lazily convert value from UUID to key if need be."""
        return LocalProxy(lambda: file_id_to_key(value))


def get_all_deposit_siblings(deposit):
    """Get all siblings of the deposit."""
    from invenio_pidstore.models import PersistentIdentifier
    from invenio_pidrelations.contrib.versioning import PIDVersioning
    recid = deposit['recid']
    rec_pid = PersistentIdentifier.get(pid_type='recid', pid_value=str(recid))
    pv = PIDVersioning(child=rec_pid)
    return [pid.get_assigned_object() for pid in pv.children]


def fetch_depid(pid):
    """Fetch depid from any pid."""
    try:
        if isinstance(pid, PersistentIdentifier):
            if pid.pid_type == 'depid':
                return pid
            elif pid.pid_type == 'recid':
                return ZenodoRecord.get_record(pid.object_uuid).depid
        elif isinstance(pid, (string_types, int)):
            return PersistentIdentifier.get('depid', pid_value=pid)
        else:
            raise Exception('"[{}] cannot be resolved to depid'.format(pid))
    except Exception:
        # FIXME: Handle or let it bubble
        pass


def delete_record(record_uuid, reason, user):
    """Delete the record and it's PIDs.

    :param record_uuid: UUID of the record to be removed.
    :param reason: Reason for removal. Either one of: 'spam', 'uploader',
        'takedown' (see 'ZENODO_REMOVAL_REASONS' variable in config),
        otherwise using it as a verbatim "Reason" string.
    :param user: ID or email of the Zenodo user (admin)
        responsible for the removal.
    """
    from invenio_github.models import ReleaseStatus
    if isinstance(user, text_type):
        user_id = User.query.filter_by(email=user).one().id
    elif isinstance(user, int):
        user_id = User.query.get(user).id
    else:
        raise TypeError("User cannot be determined from argument: {0}".format(
            user))

    record = ZenodoRecord.get_record(record_uuid)

    # Remove the record from versioning and delete the recid
    recid = PersistentIdentifier.get('recid', record['recid'])
    pv = PIDVersioning(child=recid)
    pv.remove_child(recid)
    pv.update_redirect()
    recid.delete()

    # Remove the record from index
    try:
        RecordIndexer().delete(record)
    except NotFoundError:
        pass

    # Remove buckets
    record_bucket = record.files.bucket
    RecordsBuckets.query.filter_by(record_id=record.id).delete()
    record_bucket.locked = False
    record_bucket.remove()

    removal_reasons = dict(current_app.config['ZENODO_REMOVAL_REASONS'])
    if reason in removal_reasons:
        reason = removal_reasons[reason]

    depid, deposit = deposit_resolver.resolve(record['_deposit']['id'])

    try:
        doi = PersistentIdentifier.get('doi', record['doi'])
    except PIDDoesNotExistError:
        doi = None

    # Record OpenAIRE info
    try:
        original_id = openaire_original_id(record, openaire_type(record))[1]
        datasource_id = openaire_datasource_id(record)
    except PIDDoesNotExistError:
        original_id = None
        datasource_id = None

    if pv.children.count() == 0:
        conceptrecid = PersistentIdentifier.get('recid',
                                                record['conceptrecid'])
        conceptrecid.delete()
        new_last_child = None
    else:
        new_last_child = (pv.last_child.pid_value,
                          str(pv.last_child.object_uuid))

    if 'conceptdoi' in record:
        conceptdoi_value = record['conceptdoi']
    else:
        conceptdoi_value = None

    # Completely delete the deposit
    # Deposit will be removed from index
    deposit.delete(delete_published=True)

    # Clear the record and put the deletion information
    record.clear()
    record.update({
        'removal_reason': reason,
        'removed_by': user_id,
    })
    record.commit()

    # Mark the relevant GitHub Release as deleted
    for ghr in record.model.github_releases:
        ghr.status = ReleaseStatus.DELETED

    db.session.commit()

    # After successful DB commit, sync the DOIs with DataCite
    datacite_inactivate.delay(doi.pid_value)
    if conceptdoi_value:
        if new_last_child:
            # Update last child (updates also conceptdoi)
            pid_value, rec_uuid = new_last_child
            datacite_register.delay(pid_value, rec_uuid)
        else:
            datacite_inactivate.delay(conceptdoi_value)

    # Also delete from OpenAIRE index
    if current_app.config['OPENAIRE_DIRECT_INDEXING_ENABLED'] and original_id \
            and datasource_id:
        openaire_delete.delay(original_id=original_id,
                              datasource_id=datasource_id)


def suggest_language(q, limit=5):
    """Get language suggestions based on query q from a fixed dictionary.

    :param q: Query string to look for (e.g. 'Polish', 'ger', 'english')
    :type q: str
    :param limit: limit the result to 'limit' items
    :type limit: int
    :return: list of pycountry.db.Language
    """
    q = q.lower().strip()
    lut = None
    langs = []
    # If query is 2 or 3 char long, lookup for the ISO code
    if 2 <= len(q) <= 3:
        try:
            lut = pycountry.languages.lookup(q)
        except LookupError:
            pass
    # For queries longer than 2 characters, search by name
    if len(q) > 2:
        langs = list(itertools.islice(
            (l for l in pycountry.languages if q in l.name.lower()), limit))
    # Include the ISO-fetched language (if available) on first position
    if lut:
        langs = ([lut, ] + [l for l in langs if l != lut])[:limit]
    return langs
