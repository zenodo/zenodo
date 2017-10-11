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

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers import json_v1

RELATION_TO_SCHOLIX = {
    'isCitedBy': 'IsReferencedBy',
    'cites': 'References',
    'isReferencedBy': 'IsReferencedBy',
    'references': 'References',
    'isSupplementTo': 'isSupplementTo',
    'isSupplementedBy': 'isSupplementedBy',
}


IGNORED_RECORD_KEYS = ['_deposit']


def _mock_record_relation_event_payload(record):
    return {
        'action': 'added',
        'link_provider': {'name': 'Zenodo'},
        'relationship_type': {
            'scholix_relationship': 'References',
            'original_relationship_name': 'cites',
            'original_relationship_schema': 'DataCite',
        },
        'license_url': 'https://creativecommons.org/publicdomain/zero/1.0/',
        'source': {
            'identifier': {
                'id': record.get('doi'),
                'id_schema': 'DOI',
                'id_url': 'https://doi.org',
            },
            'type': {
                'name': 'literature',
                'sub_type': 'publication-article',
                # FIXME: This?
                'sub_type_schema':
                    'https://zenodo.org/schemas/records/record-v1.0.0.json#'
                    '/resource_type/subtype',
            },
            'publisher': {'name': 'Zenodo'},
            'publication_date': record.get('publication_date'),
        },
        # corner.py v2.0.0
        'target': {
            'identifier': {
                'id': '10.5281/zenodo.53155',
                'id_schema': 'DOI',
                'id_url': 'https://doi.org',
            },
        },
    }


def format_identifer(identifier, scheme):
    result = {'id': identifier, 'id_schema': scheme.upper()}
    if scheme == 'doi':
        result['id_url'] = 'https://doi.org'
    return result


# TODO: Make this a namedtuple?
def rel_ids_set(record):
    rel_ids = record.get('related_identifiers', [])
    return {(ri['identifier'], ri['scheme'], ri['relation']) for ri in rel_ids}


def format_record_relation_event(source, identifier, scheme, relation):
    return {
        'link_provider': {'name': 'Zenodo'},
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


def extract_record_relation_events(record):
    events = defaultdict(list)
    source = {
        'identifier': format_identifer(record.get('doi'), 'doi'),
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

    # If first publication, just add everything
    # TODO: Also include versioning info (conceptdoi, etc)?
    rel_ids = rel_ids_set(record)
    if len(record.revisions) == 1:
        for identifier, scheme, relation in rel_ids:
            events['relation_created'].append(format_record_relation_event(
                source, identifier, scheme, relation))
        return events

    # Start diffing
    old_rel_ids = rel_ids_set(record.revisions[-2])

    # First deletions
    removed_rel_ids = old_rel_ids - rel_ids
    for identifier, scheme, relation in removed_rel_ids:
        events['relation_deleted'].append(format_record_relation_event(
            source, identifier, scheme, relation))

    # Then removals
    added_rel_ids = rel_ids - old_rel_ids
    for identifier, scheme, relation in added_rel_ids:
        events['relation_created'].append(format_record_relation_event(
            source, identifier, scheme, relation))
    return events


def extract_record_event(record):
    """Extract record events from a record."""
    events = {}

    # Exit early if there are no changes
    if len(record.revisions) > 1:
        record_changes = diff(
            record, record.revisions[-2], ignore=IGNORED_RECORD_KEYS)
        if not list(record_changes):
            return events

    first_publish = (record.get('_deposit', {}).get('pid', {})
                     .get('revision_id')) == 0
    # TODO: Define payload for create/update/delete
    event_type = 'record_{}'.format('created' if first_publish else 'updated')
    return {event_type: [{
        'pid': {'pid_value': record.get('doi'), 'pid_type': 'doi'},
        'metadata': json_v1.transform_record(record.pid, record)
    }]}


def generate_record_publish_events(record_id):
    """Generate all relevant events for record publishing."""
    record = ZenodoRecord.get_record(record_id)

    events = {}
    # NOTE: These functions return a Dict[str:event_type -> List[dict]]
    events.update(extract_record_event(record))
    events.update(extract_record_relation_events(record))
    return events
