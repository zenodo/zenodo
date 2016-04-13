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
    transform_dictionary(result, ['doi'], obj, ['metadata', 'doi'])
    transform_dictionary(result, ['isbn'], obj, ['metadata', 'imprint_isbn'])
    transform_dictionary(result, ['altmetric_id'],
                         obj, ['metadata', 'altmetric_id'])
    set_value_dictionary(result, ['resource_type'], get_resource_type(obj))
    transform_dictionary(result, ['publication_date'],
                         obj, ['metadata', 'publication_date'])
    transform_dictionary(result, ['publication_type'],
                         obj, ['metadata', 'publication_type'])
    transform_dictionary(result, ['title'], obj, ['metadata', 'title'])
    set_value_dictionary(result, ['creators'], get_creators(obj))
    transform_dictionary(result, ['description'],
                         obj, ['metadata', 'description'])
    transform_dictionary(result, ['keywords'], obj, ['metadata', 'keywords'])
    set_value_dictionary(result, ['subjects'], get_subjects(obj))
    transform_dictionary(result, ['notes'], obj, ['metadata', 'notes'])
    transform_dictionary(result, ['access_right'],
                         obj, ['metadata', 'access_right'])
    transform_dictionary(result, ['embargo_date'],
                         obj, ['metadata', 'embargo_date'])
    transform_dictionary(result, ['access_conditions'],
                         obj, ['metadata', 'access_conditions'])
    set_value_dictionary(result, ['license'], get_license(obj))
    set_value_dictionary(result, ['communities'], get_communities(obj)),
    # TODO provisional_communities: Add a flag provisionally.
    set_value_dictionary(result, ['grants'], get_grants(obj))
    set_value_dictionary(result, ['related_identifiers'],
                         get_related_identifiers(obj))
    set_value_dictionary(result, ['alternate_identifiers'],
                         get_alternate_identifiers(obj)),
    set_value_dictionary(result, ['contributors'], get_contributors(obj))
    set_value_dictionary(result, ['references'], get_references(obj))
    set_value_dictionary(result, ['journal'], get_journal(obj))
    set_value_dictionary(result, ['meetings'], get_meetings(obj))
    set_value_dictionary(result, ['part_of'], get_part_of(obj))
    set_value_dictionary(result, ['imprint'], get_imprint(obj))
    transform_dictionary(result, ['thesis_university'],
                         obj, ['metadata', 'thesis_university'])
    set_value_dictionary(result, ['thesis_supervisors'],
                         get_thesis_supervisors(obj))
    set_value_dictionary(result, ['files'], get_files(obj))
    transform_dictionary(result, ['owners'],
                         obj, ['owner'], lambda o: [o])
    return result


def get_resource_type(obj):
    """Parse the resource_type field."""
    resource_type = get_value_dictionary(obj, ['metadata', 'upload_type'])

    if resource_type == 'publication':
        resource_subtype = get_value_dictionary(
                obj, ['metadata', 'publication_type'])
    elif resource_type == 'image':
        resource_subtype = get_value_dictionary(obj, ['metadata', 'image_type'])
    else:
        resource_subtype = None

    return {
        'type': resource_type,
        'subtype': resource_subtype,
    }


def parse_person(person):
    """Parse a person field."""
    result = person.copy()
    transform_dictionary(result, ['familyname'],
                         person, ['name'], lambda x: x.split(',')[0])
    transform_dictionary(result, ['givennames'],
                         person, ['name'], lambda x: x.split(',')[1])
    return result


def get_creators(obj):
    """Parse the creators field."""
    return get_list(obj, ['metadata', 'creators'], lambda p: parse_person(p))


def parse_subject(subject):
    """Parse a subject."""
    result = {}
    transform_dictionary(result, ['term'], subject, ['term'])
    transform_dictionary(result, ['identifier'], subject, ['identifier'])
    transform_dictionary(result, ['scheme'], subject, ['scheme'])
    return result


def get_subjects(obj):
    """Parse the subjects field."""
    return get_list(obj, ['metadata', 'subjects'],
                    lambda s: parse_subject(s))


def get_license(obj):
    """Parse the license field."""
    result = {}
    transform_dictionary(result, ['identifier'], obj, ['metadata', 'license'])
    transform_dictionary(result, ['license'], obj, ['metadata', 'license'])
    transform_dictionary(result, ['source'], obj, ['metadata', 'source'])
    # transform_dictionary(result, ['url'], obj, ['metadata', 'url'])
    return result


def get_communities(obj):
    """Parse the communities field."""
    return get_list(obj, ['metadata', 'communities'],
                    lambda c: c['identifier'])


def get_grants(obj):
    """Parse the grants field."""
    return get_list(obj, ['metadata', 'grants'], lambda g: g['id'])


def parse_related_identifier(identifier):
    """Parse a related identifier."""
    if identifier['relation'] != 'isAlternateIdentifier':
        result = {}
        transform_dictionary(result, ['relation'], identifier, ['relation'])
        # transform_dictionary(result, ['scheme'], identifier, ['scheme'])
        transform_dictionary(result, ['identifier'], identifier, ['identifier'])
        return result
    else:
        return None


def get_related_identifiers(obj):
    """Parse the related_identifiers field."""
    return get_list(obj, ['metadata', 'related_identifiers'],
                    lambda r: parse_related_identifier(r))


def parse_alternate_ideintifier(identifier):
    """Parse an alternate identifier."""
    if identifier['relation'] == 'isAlternateIdentifier':
        result = {}
        # transform_dictionary(result, ['scheme'], identifier, ['scheme'])
        transform_dictionary(result, ['identifier'], identifier, ['identifier'])
        return result
    else:
        return None


def get_alternate_identifiers(obj):
    """Parse the alternate_identifiers field."""
    return get_list(obj, ['metadata', 'related_identifiers'],
                    lambda a: parse_alternate_ideintifier(a))


def parse_contributor(contributor):
    """Parse a contributor."""
    result = parse_person(contributor)
    transform_dictionary(result, ['type'], contributor, ['type'])
    return result


def get_contributors(obj):
    """Parse the contributors field."""
    return get_list(obj, ['metadata', 'contributors'],
                    lambda c: parse_contributor(c))


def get_references(obj):
    """Parse the deposition files field."""
    return get_list(obj, ['metadata', 'references'],
                    lambda r: {'raw_reference': r})


def get_journal(obj):
    """Parse the journal field."""
    result = {}
    transform_dictionary(result, ['issue'], obj, ['metadata', 'journal_issue'])
    transform_dictionary(result, ['pages'], obj, ['metadata', 'journal_pages'])
    transform_dictionary(result, ['title'], obj, ['metadata', 'journal_title'])
    transform_dictionary(result, ['volume'],
                         obj, ['metadata', 'journal_volume'])
    transform_dictionary(result, ['year'],
                         obj, ['metadata', 'publication_date'])
    return result


def get_meetings(obj):
    """Parse the meetings field."""
    result = {}
    transform_dictionary(result, ['title'], obj,
                         ['metadata', 'conference_title'])
    transform_dictionary(result, ['acronym'],
                         obj, ['metadata', 'conference_acronym'])
    transform_dictionary(result, ['dates'],
                         obj, ['metadata', 'conference_dates'])
    transform_dictionary(result, ['place'],
                         obj, ['metadata', 'conference_place'])
    transform_dictionary(result, ['session'],
                         obj, ['metadata', 'conference_session'])
    transform_dictionary(result, ['session_part'],
                         obj, ['metadata', 'conference_session_part'])
    transform_dictionary(result, ['url'],
                         obj, ['metadata', 'conference_url'])
    return result


def get_part_of(obj):
    """Parse the part_of fields."""
    result = {}
    transform_dictionary(result, ['title'],
                         obj, ['metadata', 'partof_title'])
    transform_dictionary(result, ['pages'],
                         obj, ['metadata', 'partof_pages'])
    transform_dictionary(result, ['publisher'],
                         obj, ['metadata', 'imprint_publisher'])
    transform_dictionary(result, ['isbn'],
                         obj, ['metadata', 'imprint_isbn'])
    transform_dictionary(result, ['place'],
                         obj, ['metadata', 'imprint_place'])
    transform_dictionary(result, ['year'],
                         obj, ['metadata', 'publication_date'])
    return result


def get_imprint(obj):
    """Parse the imprint fields."""
    result = {}
    transform_dictionary(result, 'publisher',
                         obj, ['metadata', 'imprint_publisher'])
    transform_dictionary(result, 'place',
                         obj, ['metadata', 'imprint_place'])
    return result


def get_thesis_supervisors(obj):
    """Parse the thesis_supervisors field."""
    return get_list(obj, ['metadata', 'thesis_supervisors'],
                    lambda s: parse_person(s))


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
