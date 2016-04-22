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

"""Zenodo current JSON schema to Zenodo legacy schema translator."""


from flask import url_for


def translate(obj):
    """Translate an object from legacy to zenodo schema."""
    return {
        'created': '',  # record.created
        'doi': obj['doi'],
        'doi_url': '',  # TODO doi_url
        'files': '',
        'id': obj['recid'],  # pid.pid_value
        'metadata': get_metadata(obj),
        'modified': '',  # record.updated
        'owner': get_owner(obj),
        'state': '',  #
        'submitted': False,
        'title': obj['title'],
        'record_id': '',  # recid
        'record_url': url_for('', obj['recid']),  # TODO url_for
    }


def get_files(obj):
    """."""
    pass


def get_metadata(obj):
    """."""
    return {
        'upload_type': obj['resource_type']['type'],
        'publication_type': get_publication_type(obj),
        'image_type': get_image_type(obj),
        'publication_date': obj['metadata']['publication_date'],
        'title': obj['title'],
        'creators': get_creators(obj),
        'description': obj['description'],
        'access_right': obj['access_right'],
        'license': get_license(obj),
        'embargo_date': obj['embargo_date'],
        'access_conditions': obj['access_conditions'],
        'doi': obj['doi'],
        'prereserve_doi': '',  # TODO prereserve_doi
        'keywords': obj['metadata']['keywords'],
        'notes': obj['notes'],
        'related_identifiers': get_related_identifiers(obj),
        'contributors': get_contributors(obj),
        'references': get_references(obj),
        'communities': get_communities(obj),
        'grants': get_grants(obj),
        'subjects': get_subjects(obj),
        'journal_title': obj['journal']['title'],
        'journal_volume': obj['journal']['volume'],
        'journal_issue': obj['journal']['issue'],
        'journal_pages': obj['journal']['pages'],
        'conference_title': obj['conferences']['title'],
        'conference_acronym': obj['conferences']['acronym'],
        'conference_dates': obj['conferences']['dates'],
        'conference_place': obj['conferences']['place'],
        'conference_url': obj['conferences']['url'],
        'conference_session': obj['conferences']['session'],
        'conference_session_part': obj['conferences']['session_part'],
        'imprint_publisher': obj['part_of']['publisher'],
        'imprint_isbn': obj['isbn'],
        'imprint_place': obj['part_of']['place'],
        'partof_title': obj['part_of']['title'],
        'partof_pages': obj['part_of']['pages'],
        'thesis_supervisors': get_supervisors(obj),
        'thesis_university': obj['thesis_university'],
    }


def parse_person(person):
    """."""
    result = person.copy()
    result.pop('familyname', None)
    result.pop('givenname', None)
    return result


def get_publication_type(obj):
    """."""
    return obj['resource_type']['subtype'] if (
        obj['resource_type']['type'] == 'publication') else None


def get_image_type(obj):
    """."""
    return obj['resource_type']['subtype'] if (
        obj['resource_type']['type'] == 'image') else None


def get_creators(obj):
    """."""
    result = []

    for creator in obj['metadata']['creators']:
        person = parse_person(creator)
        result.append(person)

    return result


def get_license(obj):
    """."""
    return obj['license']['license']


def get_related_identifiers(obj):
    """."""
    return obj['related_identifiers']


def get_contributors(obj):
    """."""
    result = []
    for contributor in obj['contributors']:
        person = parse_person(contributor)
        person.pop('type', None)
        result.append(person)
    return result


def get_references(obj):
    """."""
    result = []

    for reference in obj['references']:
        result.append(reference['raw_reference'])

    return result


def get_communities(obj):
    """."""
    result = ''
    for community in obj['communities'].split('\n'):
        result += '{0}\n'.format(community['identifier'])
    return result


def get_grants(obj):
    """."""
    result = []

    for grant in obj['grants']:
        result.append({
            'id': grant,
        })

    return result


def get_subjects(obj):
    """."""
    result = []

    for subject in obj['subjects']:
        result.append({
            'term': subject['term'],
            'id': subject['identifier'],
            'scheme': subject['scheme'],
        })

    return result


def get_supervisors(obj):
    """."""
    result = []
    for supervisor in obj['metadata']['thesis_supervisors']:
        person = parse_person(supervisor)
        result.append(person)
    return result


def get_owner(obj):
    """."""
    if len(obj['owners']) > 0:
        return obj['owners'][0]

    return None
