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


def get_value_dictionary(dictionary, key):
    """Get a value from a dictionary."""
    if key[0] in dictionary:
        value = dictionary[key[0]]
        return value if len(key) == 1 else get_value_dictionary(value, key[1:])
    else:
        return None


def set_value_dictionary(dictionary, key, value, function=lambda x: x,
                         required=False):
    """Set a value in a dictionary if the value is not None."""
    if required and not value:
        raise AssertionError()
    elif not value:
        return

    if len(key) == 1:
        dictionary[key[0]] = value
    else:
        # sub_key = key[0]
        # if sub_key not in dictionary:
        #     dictionary[sub_key] = {}
        set_value_dictionary(dictionary, key[1:], function(value))


def transform_dictionary(dictionary_result, key_result, dictionary_value,
                         key_value, function=lambda x: x, required=False):
    """Get a value of a dictionary and copy it into another dictionary."""
    value = get_value_dictionary(dictionary_value, key_value)
    if not value:
        return
    set_value_dictionary(dictionary_result, key_result, value, function,
                         required)


def get_list(dictionary_value, key_value, function, required=False):
    """Get a list of items from a dictionary and applies a function."""
    values = get_value_dictionary(dictionary_value, key_value)
    if values == None:
        return None

    result = []
    for item in values:
        result_item = function(item)
        if result_item:
            result.append(result_item)
    return result


def translate(obj):
    """Translate an object from legacy to zenodo schema."""
    result = {}
    transform_dictionary(result, ['doi'], obj, ['doi'])
    set_value_dictionary(result, ['files'], get_files(obj))
    set_value_dictionary(result, ['metadata'], get_metadata(obj))
    set_value_dictionary(result, ['owner'], get_owner(obj))
    set_value_dictionary(result, ['submitted'], False)
    transform_dictionary(result, ['title'], obj, ['title'])
    transform_dictionary(result, ['record_id'], obj, ['recid'])
    return result


def get_files(obj):
    """Parse the files field."""
    return []


def get_metadata(obj):
    """Parse the metadata field."""
    result = {}
    transform_dictionary(result, ['upload_type'],
                         obj, ['resource_type', 'type'])
    set_value_dictionary(result, ['publication_type'],
                         get_publication_type(obj))
    set_value_dictionary(result, ['image_type'], get_image_type(obj))
    transform_dictionary(result, ['metadata', 'publication_date'],
                         obj, ['publication_date'])
    transform_dictionary(result, ['title'], obj, ['title'])
    set_value_dictionary(result, ['creators'], get_creators(obj))
    transform_dictionary(result, ['description'], obj, ['description'])
    transform_dictionary(result, ['access_right'], obj, ['access_right'])
    transform_dictionary(result, ['license'],
                         obj, ['license', 'license'])
    transform_dictionary(result, ['embargo_date'], obj, ['embargo_date'])
    transform_dictionary(result, ['access_conditions'],
                         obj, ['access_conditions'])
    transform_dictionary(result, ['doi'], obj, ['doi'])
    set_value_dictionary(result, ['prereserve_doi'], get_prereserve_doi(obj))
    transform_dictionary(result,  ['metadata', 'keywords'], obj, ['keywords'])
    transform_dictionary(result, ['notes'], obj, ['notes'])
    set_value_dictionary(result, ['related_identifiers'],
                         get_related_identifiers(obj))
    set_value_dictionary(result, ['contributors'], get_contributors(obj))
    set_value_dictionary(result, ['references'], get_references(obj))
    set_value_dictionary(result, ['communities'], get_communities(obj))
    set_value_dictionary(result, ['grants'], get_grants(obj))
    set_value_dictionary(result, ['subjects'], get_subjects(obj))
    transform_dictionary(result, ['journal_title'], obj, ['journal', 'title'])
    transform_dictionary(result, ['journal_volume'], obj, ['journal', 'volume'])
    transform_dictionary(result, ['journal_issue'], obj, ['journal', 'issue'])
    transform_dictionary(result, ['journal_pages'], obj, ['journal', 'pages'])
    transform_dictionary(result, ['conference_title'],
                         obj, ['meetings', 'title'])
    transform_dictionary(result, ['conference_acronym'],
                         obj, ['meetings', 'acronym'])
    transform_dictionary(result, ['conference_dates'],
                         obj, ['meetings', 'dates'])
    transform_dictionary(result, ['conference_place'],
                         obj, ['meetings', 'place'])
    transform_dictionary(result, ['conference_url'],
                         obj, ['meetings', 'url'])
    transform_dictionary(result, ['conference_session'],
                         obj, ['meetings', 'session'])
    transform_dictionary(result, ['conference_session_part'],
                         obj, ['meetings', 'session_part'])
    transform_dictionary(result, ['imprint_publisher'],
                         obj, ['part_of', 'publisher'])
    transform_dictionary(result, ['imprint_isbn'], obj, ['isbn'])
    transform_dictionary(result, ['imprint_place'], obj, ['part_of', 'place'])
    transform_dictionary(result, ['partof_title'], obj, ['part_of', 'title'])
    transform_dictionary(result, ['partof_pages'], obj, ['part_of', 'pages'])
    set_value_dictionary(result, ['thesis_supervisors'], get_supervisors(obj))
    transform_dictionary(result, ['thesis_university'],
                         obj, ['thesis_university'])
    return result


def parse_person(person):
    """Parse a person field."""
    result = person.copy()
    result.pop('familyname', None)
    result.pop('givennames', None)
    return result


def get_publication_type(obj):
    """Parse the publication_type field."""
    return get_value_dictionary(obj, ['resource_type', 'subtype']) if (
        get_value_dictionary(obj, ['resource_type', 'type']) == 'publication'
    ) else None


def get_image_type(obj):
    """Parse the image_type field."""
    return get_value_dictionary(obj, ['resource_type', 'subtype']) if (
        get_value_dictionary(obj, ['resource_type', 'type']) == 'image'
    ) else None


def get_creators(obj):
    """Parse the creators field."""
    return get_list(obj, ['creators'], lambda c: parse_person(c))


def get_prereserve_doi(obj):
    """Parse the prereserve_doi field."""
    return get_value_dictionary(obj, ['doi']) is not None


def parse_alternate_identifier(alternate_identifier):
    """Parse a related_identifier."""
    alternate_identifier['relation'] = 'isAlternateIdentifier'
    return alternate_identifier


def get_related_identifiers(obj):
    """Parse the related_identifiers field."""
    alternate_identifiers = get_list(obj, ['alternate_identifiers'],
                                     lambda i: parse_alternate_identifier)

    related_identifiers = get_value_dictionary(obj, ['related_identifiers'])

    if alternate_identifiers and related_identifiers:
        return alternate_identifiers + related_identifiers
    elif alternate_identifiers:
        return alternate_identifiers
    elif related_identifiers:
        return related_identifiers
    else:
        return None


def get_contributors(obj):
    """Parse the contributors field."""
    return get_list(obj, ['contributors'], lambda c: parse_person(c))


def get_references(obj):
    """Parse the references field."""
    return get_list(obj, ['references'], lambda r: r['raw_reference'])


def get_communities(obj):
    """Parse the communities field."""
    return get_list(obj, ['communities'], lambda c: {'identifier': c})


def get_grants(obj):
    """Parse the grants field."""
    return get_list(obj, ['grants'], lambda g: {'id': g})


def parse_subject(subject):
    """Parse a subject."""
    result = {}
    transform_dictionary(result, ['term'], subject, ['term'])
    transform_dictionary(result, ['identifier'], subject, ['identifier'])
    transform_dictionary(result, ['scheme'], subject, ['scheme'])
    return result


def get_subjects(obj):
    """Parse the subjects field."""
    return get_list(obj, ['subjects'], lambda s: parse_subject(s))


def get_supervisors(obj):
    """Parse the supervisors field."""
    return get_list(obj, ['thesis_supervisors'],
                    lambda s: parse_person(s))


def get_owner(obj):
    """Parse the owner field."""
    owners = get_value_dictionary(obj, ['owners'])
    if owners and len(obj['owners']) > 0:
        return obj['owners'][0]

    return None
