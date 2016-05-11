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

from datetime import date

from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record

from zenodo.modules.records.serializers import marcxml_v1


def test_full_record(app, full_record):
    """Test full record."""
    assert Record(full_record).validate() is None
    full_record['alternate_identifiers'] = [
        {
            "identifier": "urn:lsid:ubio.org:namebank:11815",
            "scheme": "lsid",
        },
        {
            "identifier": "2011ApJS..192...18K",
            "scheme": "issn",
        },
        {
            "identifier": "10.1234/alternate.doi",
            "scheme": "doi",
        },
    ]
    assert Record(full_record).validate() is None
    full_record['meeting'] = {
        'title': 'The 13th Biennial HITRAN Conference',
        'place': 'Harvard-Smithsonian Center for Astrophysics',
        'dates': '23-25 June, 2014',
        'acronym': 'HITRAN13',
        'session': 'VI',
        'session_part': '1',
    }
    assert Record(full_record).validate() is None
    full_record['creators'] = [
        {'name': 'Doe, John', 'affiliation': 'CERN',
         'gnd': '170118215', 'orcid': '0000-0002-1694-233X',
         'familyname': 'Doe', 'givennames': 'John',
         },
        {'name': 'Doe, Jane', 'affiliation': 'CERN',
         'gnd': '', 'orcid': '0000-0002-1825-0097',
         'familyname': 'Doe', 'givennames': 'Jane',
         },
        {'name': 'Smith, John', 'affiliation': 'CERN',
         'gnd': '', 'orcid': '',
         'familyname': 'Smith', 'givennames': 'John',
         },
        {'name': 'Nowak, Jack', 'affiliation': 'CERN',
         'gnd': '170118215', 'orcid': '',
         'familyname': 'Nowak', 'givennames': 'Jack',
         },
    ]
    assert Record(full_record).validate() is None
    full_record['contributors'] = [
        {'affiliation': 'CERN', 'name': 'Smith, Other', 'type': 'Other',
         'gnd': '', 'orcid': '0000-0002-1825-0097'},
        {'affiliation': '', 'name': 'Hansen, Viggo', 'type': 'Other',
         'gnd': '', 'orcid': ''},
        {'affiliation': 'CERN', 'name': 'Kowalski, Manager',
         'type': 'DataManager'},
    ]
    full_record['thesis']['supervisors'] = [
        {'name': 'Smith, Professor'},
    ]
    assert Record(full_record).validate() is None
    full_record['description'] = 'Test Description'
    assert Record(full_record).validate() is None
    full_record['related_identifiers'] = [
        {"identifier": "10.1234/foo.bar", "scheme": "doi",
         "relation": "cites"},
        {"identifier": "1234.4321", "scheme": "arxiv", "relation": "cites"},
    ]
    assert Record(full_record).validate() is None
    full_record['references'] = [
        {'raw_reference': 'Doe, John et al (2012). Some title. Zenodo. '
         '10.5281/zenodo.12'},
        {'raw_reference': 'Smith, Jane et al (2012). Some title. Zenodo. '
         '10.5281/zenodo.34'},
    ]
    assert Record(full_record).validate() is None
    full_record['embargo_date'] = '0900-12-31'
    assert Record(full_record).validate() is None
    full_record['_oai'] = {
        "id": "oai:zenodo.org:1",
        "sets": ["user-zenodo", "user-ecfunded"]
    }
    assert Record(full_record).validate() is None
    full_record['embargo_date'] = '0900-12-31'
    assert Record(full_record).validate() is None
    full_record['_oai'] = {
        "id": "oai:zenodo.org:1",
        "sets": ["user-zenodo", "user-ecfunded"]
    }
    assert Record(full_record).validate() is None
    record = Record(full_record)
    pid = PersistentIdentifier(pid_type='recid', pid_value='2')
    data = marcxml_v1.schema_class().dump(marcxml_v1.preprocess_record(
        pid=pid,
        record=record)).data
    marcxml_v1.serialize(
        pid=PersistentIdentifier(pid_type='recid', pid_value='2'),
        record=Record(full_record))
    expected = {
        u'terms_governing_use_and_reproduction_note': {
            u'uniform_resource_identifier': u'http://zenodo.org',
            u'terms_governing_use_and_reproduction': u'Creative Commons'
        },
        u'publication_distribution_imprint': {
            u'date_of_publication_distribution': u'2014-02-27'
        },
        u'subject_added_entry_topical_term': {
            u'topical_term_or_geographic_name_entry_element': u'cc-by',
            u'source_of_heading_or_term': u'opendefinition.org'
        },
        u'general_note': {
            u'general_note': u'notes'
        },
        u'control_number': u'12345',
        u'information_relating_to_copyright_status': {
            u'copyright_status': u'open'
        },
        u'title_statement': {
            u'title': u'Test title'
        },
        u'index_term_uncontrolled': {
            u'uncontrolled_term': [u'kw1', u'kw2', u'kw3']
        },
        u'communities': [
            u'zenodo'
        ],
        u'other_standard_identifier': [
            {
                u'standard_number_or_code':
                u'urn:lsid:ubio.org:namebank:11815',
                u'source_of_number_or_code': u'lsid'
            },
            {
                u'standard_number_or_code': u'2011ApJS..192...18K',
                u'source_of_number_or_code': u'issn'
            },
            {
                u'standard_number_or_code': u'10.1234/alternate.doi',
                u'source_of_number_or_code': u'doi'
            }
        ],
        u'funding_information_note': [
            {u'grant_number': u'1234', u'text_of_note': u'Grant Title'},
            {u'grant_number': u'4321', u'text_of_note': u'Title Grant'}
        ],
        u'resource_type': {
            u'subtype': u'book',
            u'type': u'publication'
        },
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
        'main_entry_personal_name': {
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
        u'host_item_entry': [
            {
                u'note': u'doi',
                u'relationship_information': u'cites',
            },
            {
                u'note': u'arxiv',
                u'relationship_information': u'cites',
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
        u'embargo_date': '0900-12-31',
        u'_oai': {
            u'sets': [u'user-zenodo', u'user-ecfunded'],
            u'id': u'oai:zenodo.org:1'
        }
    }
    check_dict(expected, data)


def test_minimal_record(app, minimal_record):
    """Test minimal record."""
    assert Record(minimal_record).validate() is None
    pid = PersistentIdentifier(pid_type='recid', pid_value='2')
    data = marcxml_v1.schema_class().dump(marcxml_v1.preprocess_record(
        pid=pid,
        record=Record(minimal_record))).data
    marcxml_v1.serialize(pid=pid, record=Record(minimal_record))
    expected = {
        u'publication_distribution_imprint': {
            'date_of_publication_distribution': date.today().isoformat()
        },
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
        }
    }
    check_dict(expected, data)


def check_array(a1, a2):
    """Check array."""
    for i in range(0, len(a1)):
        if isinstance(a1[i], dict):
            check_dict(a1[i], a2[i])
        elif isinstance(a1[i], list) or isinstance(a1[i], tuple):
            check_array(a1[i], a2[i])
        else:
            assert a1[i] in a2
    assert len(a1) == len(a2)


def check_dict(a1, a2):
    """Check dict."""
    for (k, v) in a1.items():
        assert k in a2
        if isinstance(v, dict):
            check_dict(v, a2[k])
        elif isinstance(v, list) or isinstance(v, tuple):
            check_array(v, a2[k])
        else:
            assert a2[k] == v
    assert len(a2) == len(a1)
