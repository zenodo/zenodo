# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Webhook events for Zenodo Deposit."""

from collections import defaultdict

from dictdiffer import diff
from flask import current_app
from invenio_pidrelations.contrib.versioning import PIDVersioning

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers.schemas.common import format_pid_link

RELATION_TO_SCHOLIX = {
    'isCitedBy': 'IsReferencedBy',
    'cites': 'References',
    'isReferencedBy': 'IsReferencedBy',
    'references': 'References',
    'isSupplementTo': 'isSupplementTo',
    'isSupplementedBy': 'isSupplementedBy',
}


IGNORED_RECORD_KEYS = ['_deposit', '_internal', '_files', '_oai']


def format_identifer(identifier, scheme):
    result = {'id': identifier, 'id_schema': scheme.upper()}
    if scheme == 'doi':
        result['id_url'] = 'https://doi.org'
    return result


# TODO: Make this a namedtuple?
def rel_ids_set(record):
    rel_ids = record.get('related_identifiers', [])
    return {(ri['identifier'], ri['scheme'], ri['relation']) for ri in rel_ids}


def format_record_relation_event(source, identifier, scheme, relation,
                                 publication_date=None):
    relation = {
        'relation_provider': {'name': 'Zenodo'},
        'relationship_type': {
            'scholix_relationship':
                RELATION_TO_SCHOLIX.get(relation, 'IsRelatedTo'),
            'original_relationship_name': relation,
            'original_relationship_schema': 'DataCite',
        },
        'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'source': source,
        'target': {'identifier': format_identifer(identifier, scheme)},
    }
    if publication_date:
        relation['relation_publication_date'] = publication_date
    return relation


def format_source_object(record, identifier=None, scheme=None):
    return {
        'identifier': format_identifer(
            identifier or record.get('doi'),
            scheme or 'doi'),
        'type': {
            'name': (
                'literature' if record['resource_type']['type'] != 'dataset'
                else 'dataset'),
            'sub_type':
                ObjectType.get_by_dict(record['resource_type'])['internal_id'],
            'sub_type_schema':
                'https://zenodo.org/schemas/records/record-v1.0.0.json#'
                '/resource_type/subtype',
        },
        'publisher': {'name': 'Zenodo'},
        'publication_date': record.get('publication_date'),
    }


def extract_record_relation_events(recid, record, old_record=None):
    events = defaultdict(list)
    source = format_source_object(record)

    # If first publication, just add everything
    # TODO: Also include versioning info (conceptdoi, etc)?
    rel_ids = rel_ids_set(record)
    if not old_record:
        for identifier, scheme, relation in rel_ids:
            events['relation_created'].append(format_record_relation_event(
                source, identifier, scheme, relation))

        # Also add isIdenticalTo for the Zenodo URL
        record_url = format_pid_link(
            current_app.config['RECORDS_UI_ENDPOINT'], recid.pid_value)
        events['relation_created'].append(format_record_relation_event(
            source, record_url, 'url', 'isIdenticalTo'))

        # Version relations
        pv = PIDVersioning(child=recid)
        if pv.exists:
            events['relation_created'].append(format_record_relation_event(
                source, record['conceptdoi'], 'doi', 'isPartOf'))
            # children = pv.children.all()
            # if len(children) > 1:
            #     idx = children.index(objid) if objid in children else len(children)
            #     events['relation_created'].append()
        return events

    # Start diffing
    old_rel_ids = rel_ids_set(old_record)

    # First deletions...
    removed_rel_ids = old_rel_ids - rel_ids
    for identifier, scheme, relation in removed_rel_ids:
        events['relation_deleted'].append(format_record_relation_event(
            source, identifier, scheme, relation))
    # ...then removals
    added_rel_ids = rel_ids - old_rel_ids
    for identifier, scheme, relation in added_rel_ids:
        events['relation_created'].append(format_record_relation_event(
            source, identifier, scheme, relation))
    return events


def extract_record_events(recid, record, old_record=None):
    """Extract record events from a record."""
    events = {}

    # Exit early if there are no changes
    if old_record:
        record_changes = diff(record, old_record, ignore=IGNORED_RECORD_KEYS)
        if not list(record_changes):
            return events

    event_type = 'object_{}'.format('updated' if old_record else 'created')
    events = {
        event_type: [
            {
                'object_publication_date': record.get('publication_date'),
                'object_provider': {'name': 'Zenodo'},
                'object': format_source_object(record),
                'metadata': {
                    'title': record.get('title'),
                    'creators': record.get('creators'),
                },
                'metadata_schema': 'Zenodo',
                'metadata_schema_url':
                    'https://zenodo.org/schemas/records/record-v1.0.0.json',
            }
        ]
    }
    # If the record is versioned and it's the first publication of it
    if 'conceptdoi' in record and not old_record:
        events[event_type].append({
            'object_publication_date': record.get('publication_date'),
            'object_provider': {'name': 'Zenodo'},
            'object': format_source_object(
                record, identifier=record.get('conceptdoi')),
        })
    return events


def generate_record_publish_events(record_id, revision, old_revision=None):
    """Generate all relevant events for record publishing."""
    record = ZenodoRecord.get_record(record_id)
    recid = record.pid
    # NOTE: Calling `record.revisions[revision].replace_refs()` doesn't work
    current_revision = ZenodoRecord(record.revisions[revision].model.json)
    previous_revision = (
        ZenodoRecord(record.revisions[old_revision].model.json)
        if old_revision else None)

    events = defaultdict(list)
    # NOTE: These functions return a Dict[str:event_type -> List[dict]]
    events.update(extract_record_events(
        recid, current_revision, previous_revision))
    events.update(extract_record_relation_events(
        recid, current_revision, previous_revision))
    return events
