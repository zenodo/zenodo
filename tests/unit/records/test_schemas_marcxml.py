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

"""Zenodo Marcxml mapping test."""

from __future__ import absolute_import, print_function

from datetime import datetime

from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record

from zenodo.modules.records.serializers import marcxml_v1


def test_full_record(app, db, full_record):
    """Test MARC21 serialization of full record."""
    record = Record.create(full_record)
    record.model.updated = datetime.utcnow()
    assert record.validate() is None

    # Add embargo date and OAI-PMH set information.
    full_record['embargo_date'] = '0900-12-31'
    full_record['_oai'] = {
        "id": "oai:zenodo.org:1",
        "sets": ["user-zenodo", "user-ecfunded"]
    }

    # Create record and PID.
    record = Record.create(full_record)
    pid = PersistentIdentifier(pid_type='recid', pid_value='2')
    assert record.validate() is None

    expected = {
        u'control_number': u'12345',
        u'date_and_time_of_latest_transaction': (
            record.model.updated.strftime("%Y%m%d%H%M%S.0")),
        u'resource_type': {
            u'subtype': u'book',
            u'type': u'publication'
        },
        u'title_statement': {
            u'title': u'Test title'
        },
        u'publication_distribution_imprint': [
            {u'date_of_publication_distribution': u'2014-02-27'},
        ],
        u'main_entry_personal_name': {
            u'affiliation': u'CERN',
            u'personal_name': u'Doe, John',
            u'authority_record_control_number_or_standard_number': [
                u'(gnd)170118215', u'(orcid)0000-0002-1694-233X'
            ]
        },
        u'added_entry_personal_name': [
            {
                u'affiliation': u'CERN',
                u'personal_name': u'Doe, Jane',
                u'authority_record_control_number_or_standard_number': [
                    u'(orcid)0000-0002-1825-0097'
                ]
            },
            {
                u'affiliation': u'CERN',
                u'personal_name': u'Smith, John',
            },
            {
                u'affiliation': u'CERN',
                u'personal_name': u'Nowak, Jack',
                u'authority_record_control_number_or_standard_number': [
                    u'(gnd)170118215'
                ]
            },
            {
                u'affiliation': u'CERN',
                u'relator_code': [u'oth'],
                u'personal_name': u'Smith, Other',
                u'authority_record_control_number_or_standard_number': [
                    u'(orcid)0000-0002-1825-0097'
                ]
            },
            {
                u'personal_name': u'Hansen, Viggo',
                u'relator_code': [u'oth'],
            },
            {
                u'affiliation': u'CERN',
                u'relator_code': [u'dtm'],
                u'personal_name': u'Kowalski, Manager'
            },
            {
                u'relator_code': [u'ths'],
                u'personal_name': u'Smith, Professor'
            },
        ],
        u'summary': {
            u'summary': u'Test Description'
        },
        u'index_term_uncontrolled': [
            {u'uncontrolled_term': u'kw1'},
            {u'uncontrolled_term': u'kw2'},
            {u'uncontrolled_term': u'kw3'},
        ],
        u'subject_added_entry_topical_term': [
            {
                u'topical_term_or_geographic_name_entry_element': u'cc-by',
                u'source_of_heading_or_term': u'opendefinition.org',
                u'level_of_subject': u'Primary',
                u'thesaurus': u'Source specified in subfield $2',
            },
            {
                u'topical_term_or_geographic_name_entry_element': u'Astronomy',
                u'authority_record_control_number_or_standard_number': (
                    u'(url)http://id.loc.gov/authorities/subjects/sh85009003'),
                u'level_of_subject': u'Primary',
            },

        ],
        u'general_note': {
            u'general_note': u'notes'
        },
        u'information_relating_to_copyright_status': {
            u'copyright_status': u'open'
        },
        u'terms_governing_use_and_reproduction_note': {
            u'uniform_resource_identifier': u'http://zenodo.org',
            u'terms_governing_use_and_reproduction': u'Creative Commons'
        },
        u'communities': [
            u'zenodo',
        ],
        u'funding_information_note': [
            {u'grant_number': u'1234', u'text_of_note': u'Grant Title'},
            {u'grant_number': u'4321', u'text_of_note': u'Title Grant'}
        ],
        u'host_item_entry': [
            {
                u'main_entry_heading': u'10.1234/foo.bar',
                u'note': u'doi',
                u'relationship_information': u'cites',
            },
            {
                u'main_entry_heading': u'1234.4321',
                u'note': u'arxiv',
                u'relationship_information': u'cites',
            },
            {
                u'main_entry_heading': u'Staszkowka',
                u'edition': u'Jol',
                u'title': u'Bum',
                u'related_parts': u'1-2',
                u'international_standard_book_number': u'978-0201633610',
            },
        ],
        u'other_standard_identifier': [
            {
                u'standard_number_or_code': u'10.1234/foo.bar',
                u'source_of_number_or_code': u'doi',
            },
            {
                u'standard_number_or_code': (
                    u'urn:lsid:ubio.org:namebank:11815'),
                u'source_of_number_or_code': u'lsid',
                u'qualifying_information': u'alternateidentifier',
            },
            {
                u'standard_number_or_code': u'2011ApJS..192...18K',
                u'source_of_number_or_code': u'issn',
                u'qualifying_information': u'alternateidentifier',
            },
            {
                u'standard_number_or_code': u'10.1234/alternate.doi',
                u'source_of_number_or_code': u'doi',
                u'qualifying_information': u'alternateidentifier',
            }
        ],
        u'references': [
            {
                u'raw_reference': u'Doe, John et al (2012). Some title. '
                'Zenodo. 10.5281/zenodo.12'
            }, {
                u'raw_reference': u'Smith, Jane et al (2012). Some title. '
                'Zenodo. 10.5281/zenodo.34'
            }
        ],
        u'added_entry_meeting_name': [{
            u'date_of_meeting': u'23-25 June, 2014',
            u'meeting_name_or_jurisdiction_name_as_entry_element':
            u'The 13th Biennial HITRAN Conference',
            u'number_of_part_section_meeting': u'VI',
            u'miscellaneous_information': u'HITRAN13',
            u'name_of_part_section_of_a_work': u'1',
            u'location_of_meeting':
            u'Harvard-Smithsonian Center for Astrophysics'
        }],
        u'conference_url': 'http://hitran.org/conferences/hitran-13-2014/',
        u'dissertation_note': {
            u'name_of_granting_institution': u'I guess important',
        },
        u'journal': {
            'issue': '2',
            'pages': '20',
            'volume': '20',
            'title': 'Bam',
            'year': '2014',
        },
        # missing files
        # missing language
        u'embargo_date': '0900-12-31',
        u'_oai': {
            u'sets': [u'user-zenodo', u'user-ecfunded'],
            u'id': u'oai:zenodo.org:1'
        },
        u'_files': [
            {
                'uri': 'https://zenodo.org/record/12345/files/test',
                'checksum': 'md5:11111111111111111111111111111111',
                'type': 'txt',
                'size': 4,
            },
        ],
        'leader': {
            'base_address_of_data': '00000',
            'bibliographic_level': 'monograph_item',
            'character_coding_scheme': 'marc-8',
            'descriptive_cataloging_form': 'unknown',
            'encoding_level': 'unknown',
            'indicator_count': 2,
            'length_of_the_implementation_defined_portion': 0,
            'length_of_the_length_of_field_portion': 4,
            'length_of_the_starting_character_position_portion': 5,
            'multipart_resource_record_level':
                'not_specified_or_not_applicable',
            'record_length': '00000',
            'record_status': 'new',
            'subfield_code_count': 2,
            'type_of_control': 'no_specified_type',
            'type_of_record': 'language_material',
            'undefined': 0,
        },
    }

    # Dump MARC21 JSON structure and compare against expected JSON.
    preprocessed_record = marcxml_v1.preprocess_record(record=record, pid=pid)
    assert_dict(
        expected,
        marcxml_v1.schema_class().dump(preprocessed_record).data
    )

    # Assert that we can output MARCXML.
    assert marcxml_v1.serialize(record=record, pid=pid)


def test_minimal_record(app, db, minimal_record):
    """Test minimal record."""
    # Create record and pid.
    record = Record.create(minimal_record)
    record.model.updated = datetime.utcnow()
    pid = PersistentIdentifier(pid_type='recid', pid_value='2')
    assert record.validate() is None

    expected = {
        u'date_and_time_of_latest_transaction': (
            record.model.updated.strftime("%Y%m%d%H%M%S.0")),
        u'publication_distribution_imprint': [{
            'date_of_publication_distribution': record['publication_date']
        }],
        u'control_number': '123',
        u'information_relating_to_copyright_status': {
            'copyright_status': 'open'
        },
        u'summary': {
            'summary': 'My description'
        },
        u'main_entry_personal_name': {
            'personal_name': 'Test'
        },
        u'resource_type': {
            'type': 'software'
        },
        u'title_statement': {
            'title': 'Test'
        },
        u'leader': {
            'base_address_of_data': '00000',
            'bibliographic_level': 'monograph_item',
            'character_coding_scheme': 'marc-8',
            'descriptive_cataloging_form': 'unknown',
            'encoding_level': 'unknown',
            'indicator_count': 2,
            'length_of_the_implementation_defined_portion': 0,
            'length_of_the_length_of_field_portion': 4,
            'length_of_the_starting_character_position_portion': 5,
            'multipart_resource_record_level':
                'not_specified_or_not_applicable',
            'record_length': '00000',
            'record_status': 'new',
            'subfield_code_count': 2,
            'type_of_control': 'no_specified_type',
            'type_of_record': 'computer_file',
            'undefined': 0,
        },
    }

    data = marcxml_v1.schema_class().dump(marcxml_v1.preprocess_record(
        pid=pid,
        record=record)).data
    assert_dict(expected, data)

    marcxml_v1.serialize(pid=pid, record=record)


def assert_array(a1, a2):
    """Check array."""
    for i in range(0, len(a1)):
        if isinstance(a1[i], dict):
            assert_dict(a1[i], a2[i])
        elif isinstance(a1[i], list) or isinstance(a1[i], tuple):
            assert_array(a1[i], a2[i])
        else:
            assert a1[i] in a2

    assert len(a1) == len(a2)


def assert_dict(a1, a2):
    """Check dict."""
    for (k, v) in a1.items():
        assert k in a2
        if isinstance(v, dict):
            assert_dict(v, a2[k])
        elif isinstance(v, list) or isinstance(v, tuple):
            assert_array(v, a2[k])
        else:
            assert a2[k] == v
    assert len(a2) == len(a1)
