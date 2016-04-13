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

"""Zenodo legacy to the current Zenodo JSON schema translator."""


def translate(obj):
    """Translate an object from legacy to zenodo schema."""
    return {
        # 'recid': obj ['record']['id'],
        'doi': obj['metadata']['doi'],
        'isbn': obj['metadata']['imprint_isbn'],
        'altmetric_id': '',  # TODO altmetric_id generated
        'resource_type': get_resource_type(obj),
        'publication_date': obj['metadata']['publication_date'],
        'publication_type': obj['metadata']['publication_type'],
        'title': obj['metadata']['title'],
        'creators': get_creators(obj),
        'description': obj['metadata']['description'],
        'keywords': obj['metadata']['keywords'],
        'subjects': get_subjects(obj),
        'notes': obj['metadata']['notes'],
        'access_right': obj['metadata']['access_right'],
        'embargo_date': obj['metadata']['embargo_date'],
        'access_conditions': '',  # TODO access_conditions
        'license': get_license(obj),
        'communities': get_communities(obj),
        'provisional_communities': '',  # TODO provisional add a flag
        'grants': get_grants(obj),
        'related_identifiers': get_related_identifiers(obj),
        'alternate_identifiers': get_alternate_identifiers(obj),
        'contributors': get_contributors(obj),
        'references': get_references(obj),
        'journal': get_journal(obj),
        'meetings': get_meetings(obj),
        'part_of': get_part_of(obj),
        'imprint': get_imprint(obj),
        'thesis_university': obj['metadata']['thesis_university'],
        'thesis_supervisors': get_thesis_supervisors(obj),
        'files': get_files(obj),
        'owners': [obj['owner']],
    }


def get_resource_type(obj):
    """Parse the resource_type field."""
    resource_type = obj['metadata']['upload_type']

    if resource_type == 'publication':
        resource_subtype = obj['metadata']['publication_type']
    elif resource_type == 'image':
        resource_subtype = obj['metadata']['image_type']
    else:
        resource_subtype = None
    return {
        'type': resource_type,
        'subtype': resource_subtype,
    }


def parse_person(person):
    """Parse a person field."""
    result = person.copy()
    result['familyname'] = person['name'].split(',')[0]
    result['givennames'] = person['name'].split(',')[1]
    return result


def get_creators(obj):
    """Parse the creators field."""
    result = []

    for creator in obj['metadata']['creators']:
        person = parse_person(creator)
        result.append(person)

    return result


def get_subjects(obj):
    """Parse the subjects field."""
    result = []

    for subject in obj['metadata']['subjects']:
        result.append({
            'term': subject['term'],
            'identifier': subject['identifier'],
            'scheme': subject['scheme'],
        })

    return result


def get_license(obj):
    """Parse the license field."""
    return {
        'identifier': obj['metadata']['license'],
        'license': obj['metadata']['license'],  # JSONRef
        'source': obj['metadata']['license'],
        'url': '',  # TODO url
    }


def get_communities(obj):
    """Parse the communities field."""
    result = []
    for community in obj['metadata']['communities']:
        result.append({
            'identifier': community
        })
    return result


def get_grants(obj):
    """Parse the grants field."""
    result = []
    for grant in obj['metadata']['grants']:
        result.append(grant['id'])
    return result


def get_related_identifiers(obj):
    """Parse the related_identifiers field."""
    result = []

    for related_identifier in obj['metadata']['related_identifiers']:
        if related_identifier['relation'] != 'isAlternateIdentifier':
            result.append({
                'relation': related_identifier['relation'],
                'scheme': '',  # TODO scheme
                'identifier': related_identifier['identifier'],
            })

    return result


def get_alternate_identifiers(obj):
    """Parse the alternate_identifiers field."""
    result = []

    for related_identifier in obj['metadata']['related_identifiers']:
        if related_identifier['relation'] == 'isAlternateIdentifier':
            result.append({
                'relation': related_identifier['relation'],
                'scheme': '',  # TODO scheme
                'identifier': related_identifier['identifier'],
            })

    return result


def get_contributors(obj):
    """Parse the contributors field."""
    result = []
    for contributor in obj['metadata']['contributors']:
        person = parse_person(contributor)
        person['type'] = contributor['type']
        result.append(person)
    return result


def get_references(obj):
    """Parse the deposition files field."""
    result = []
    for reference in obj['metadata']['references']:
        result.append({
            'raw_reference': reference
        })
    return result


def get_journal(obj):
    """Parse the journal field."""
    return {
        'issue': '',
        'pages': '',
        'title': '',
        'volume': '',
        'year': obj['metadata']['publication_date']
    }


def get_meetings(obj):
    """Parse the meetings field."""
    return [
        {
            'title': obj['metadata']['conference_title'],
            'acronym': obj['metadata']['conference_acronym'],
            'dates': obj['metadata']['conference_dates'],
            'place': obj['metadata']['conference_place'],
            'session': obj['metadata']['conference_session'],
            'session_part': obj['metadata']['conference_session_part'],
        },
    ]


def get_part_of(obj):
    """Parse the part_of fields."""
    return {
        'title': obj['metadata']['partof_title'],
        'pages': obj['metadata']['partof_pages'],
        'publisher': obj['metadata']['imprint_publisher'],
        'isbn': obj['metadata']['imprint_isbn'],
        'place': obj['metadata']['imprint_place'],
        'year': obj['metadata']['publication_date'],
    }


def get_imprint(obj):
    """Parse the imprint fields."""
    return {
        'publisher': obj['metadata']['imprint_publisher'],
        'place': obj['metadata']['imprint_place'],
    }


def get_thesis_supervisors(obj):
    """Parse the thesis_supervisors field."""
    result = []
    for supervisor in obj['metadata']['thesis_supervisors']:
        person = parse_person(supervisor)
        result.append(person)
    return result


def get_files(obj):
    """Parse the deposition files field."""
    # result = []
    #
    # for file in obj['files']:
    #     result.append({
    #         'bucket': '',
    #         'filename': file['filename'],
    #         'version_id': '',
    #         'size': file['filesize'],
    #         'checksum': file['checksum'],
    #         'previewer': '',
    #         'type': '',
    #     })
    #
    # return result
    return []
