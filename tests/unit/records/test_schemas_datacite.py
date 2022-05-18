# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016-2018 CERN.
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

"""Zenodo Dublin Core mapping test."""

from __future__ import absolute_import, print_function

import json
from datetime import datetime, timedelta

import pytest

from zenodo.modules.records.serializers import datacite_v31, datacite_v41


def today():
    """Get todays UTC date."""
    return datetime.utcnow().date()


def test_minimal(db, minimal_record_model, recid_pid):
    """Test minimal."""
    minimal_record_model['doi'] = '10.5072/foo'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj == {
        'identifier': {'identifier': '10.5072/foo', 'identifierType': 'DOI'},
        'creators': [{'creatorName': 'Test', 'nameIdentifier': {}}],
        'titles': [{'title': 'Test'}],
        'publisher': 'Zenodo',
        'publicationYear': str(today().year),
        'dates': [{'dateType': 'Issued', 'date': today().isoformat()}],
        'subjects': [],
        'contributors': [],
        'resourceType': {
            'resourceType': None, 'resourceTypeGeneral': 'Software'},
        'alternateIdentifiers': [{
            'alternateIdentifier': 'http://localhost/record/123',
            'alternateIdentifierType': 'url',
        }],
        'relatedIdentifiers': [],
        'rightsList': [
            {'rights': 'Open Access',
             'rightsURI': 'info:eu-repo/semantics/openAccess'}],
        'descriptions': [
            {'description': 'My description', 'descriptionType': 'Abstract'}]
    }


def test_non_local_doi(db, minimal_record_model, recid_pid):
    """Test non-local DOI."""
    minimal_record_model['doi'] = '10.1234/foo'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['identifier'] == {'identifier': 'http://localhost/record/123',
                                 'identifierType': 'URL'}
    assert obj['relatedIdentifiers'] == [{
        'relatedIdentifier': '10.1234/foo',
        'relatedIdentifierType': 'DOI',
        'relationType': 'IsIdenticalTo',
    }]


def test_full(db, record_with_bucket, recid_pid):
    """Test full record metadata."""
    _, full_record_model = record_with_bucket
    full_record_model['doi'] = '10.5072/foo'
    obj = datacite_v31.transform_record(recid_pid, full_record_model)
    expected = {
        "alternateIdentifiers": [
            {
                "alternateIdentifier": "urn:lsid:ubio.org:namebank:11815",
                "alternateIdentifierType": "lsid"
            },
            {
                "alternateIdentifier": "2011ApJS..192...18K",
                "alternateIdentifierType": "ads"
            },
            {
                'alternateIdentifier': '0317-8471',
                'alternateIdentifierType': 'issn',
            },
            {
                "alternateIdentifier": "10.1234/alternate.doi",
                "alternateIdentifierType": "doi"
            },
            {
                "alternateIdentifier": "http://localhost/record/12345",
                "alternateIdentifierType": "url"
            },
        ],
        "contributors": [
            {
                "affiliation": "CERN",
                "contributorName": "Smith, Other",
                "contributorType": "Other",
                "nameIdentifier": {
                    "nameIdentifier": "0000-0002-1825-0097",
                    "nameIdentifierScheme": "ORCID",
                    "schemeURI": "http://orcid.org/"
                }
            },
            {
                "affiliation": "",
                "contributorName": "Hansen, Viggo",
                "contributorType": "Other",
                "nameIdentifier": {}
            },
            {
                "affiliation": "CERN",
                "contributorName": "Kowalski, Manager",
                "contributorType": "DataManager",
                "nameIdentifier": {}
            }
        ],
        "creators": [
            {
                "affiliation": "CERN",
                "creatorName": "Doe, John",
                "nameIdentifier": {
                    "nameIdentifier": "0000-0002-1694-233X",
                    "nameIdentifierScheme": "ORCID",
                    "schemeURI": "http://orcid.org/"
                }
            },
            {
                "affiliation": "CERN",
                "creatorName": "Doe, Jane",
                "nameIdentifier": {
                    "nameIdentifier": "0000-0002-1825-0097",
                    "nameIdentifierScheme": "ORCID",
                    "schemeURI": "http://orcid.org/"
                }
            },
            {
                "affiliation": "CERN",
                "creatorName": "Smith, John",
                "nameIdentifier": {}
            },
            {
                "affiliation": "CERN",
                "creatorName": "Nowak, Jack",
                "nameIdentifier": {
                    "nameIdentifier": "170118215",
                    "nameIdentifierScheme": "GND"
                }
            }
        ],
        "dates": [
            {"date": "2014-02-27", "dateType": "Issued"},
            {"date": "2019-01-01/", "dateType": "Valid"},
            # NOTE: "Withdrawn" is not in the DataCite v3.1 dateType vocabulary
            # {"date": "2019-01-01", "dateType": "Withdrawn"},
            {"date": "/2019-01-01", "dateType": "Collected"},
            {"date": "2019-01-01/2019-02-01", "dateType": "Collected"},
        ],
        "descriptions": [
            {
                "description": "Test Description",
                "descriptionType": "Abstract"
            },
            {
                "description": "notes",
                "descriptionType": "Other"
            },
            {
                "description": (
                    "{\"references\": [\"Doe, John et al (2012). "
                    "Some title. Zenodo. 10.5281/zenodo.12\", \"Smith, "
                    "Jane et al (2012). Some title. Zenodo. "
                    "10.5281/zenodo.34\"]}"
                ),
                "descriptionType": "Other"
            },
            {'description': 'microscopic supersampling',
             'descriptionType': 'Methods'}
        ],
        "identifier": {"identifier": "10.5072/foo", "identifierType": "DOI"},
        "language": "en",
        "geoLocations": [{
            "geoLocationPlace": "my place",
            "geoLocationPoint": "2.35 1.534"
        }, {
            'geoLocationPlace': 'New York'
        }],
        "publicationYear": "2014",
        "publisher": "Zenodo",
        "relatedIdentifiers": [
            {
                "relationType": "Cites",
                "resourceTypeGeneral": "Dataset",
                "relatedIdentifier": "10.1234/foo.bar",
                "relatedIdentifierType": "DOI"
            },
            {
                "relationType": "IsIdenticalTo",
                "relatedIdentifier": "1234.4325",
                "relatedIdentifierType": "arXiv"
            },
            {
                "relationType": "Cites",
                "resourceTypeGeneral": "Dataset",
                "relatedIdentifier": "1234.4321",
                "relatedIdentifierType": "arXiv"
            },
            {
                "relationType": "References",
                "resourceTypeGeneral": "Dataset",
                "relatedIdentifier": "1234.4328",
                "relatedIdentifierType": "arXiv"
            },
            {
                "relationType": "IsPartOf",
                "relatedIdentifier": "10.1234/zenodo.4321",
                "relatedIdentifierType": "DOI",
                "resourceTypeGeneral": "Software"
            },
            {
                "relationType": "HasPart",
                "relatedIdentifier": "10.1234/zenodo.1234",
                "relatedIdentifierType": "DOI",
                "resourceTypeGeneral": "BookChapter"
            },
            {
                "relationType": "IsPartOf",
                "relatedIdentifier": "http://localhost/communities/zenodo",
                "relatedIdentifierType": "URL"
            }
        ],
        "resourceType": {
            "resourceType": None,
            "resourceTypeGeneral": "Book"
        },
        "rightsList": [
            {
                "rights": "Creative Commons Attribution 4.0",
                "rightsURI": "https://creativecommons.org/licenses/by/4.0/"
            },
            {
                "rights": "Open Access",
                "rightsURI": "info:eu-repo/semantics/openAccess"
            }
        ],
        "subjects": [
            {"subject": "kw1"},
            {"subject": "kw2"},
            {"subject": "kw3"},
            {
                "subject": "http://id.loc.gov/authorities/subjects/sh85009003",
                "subjectScheme": "url"
            }
        ],
        "titles": [{"title": "Test title"}],
        "version": "1.2.5"
    }
    assert obj == expected

    obj = datacite_v41.transform_record(recid_pid, full_record_model)
    expected['creators'] = [
        {
            'affiliations': ['CERN'],
            'creatorName': 'Doe, John',
            'familyName': 'Doe',
            'givenName': 'John',
            'nameIdentifiers': [
                {
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/',
                    'nameIdentifier': '0000-0002-1694-233X'
                },
                {
                    'nameIdentifierScheme': 'GND',
                    'nameIdentifier': '170118215'
                }
            ],
        },
        {
            'affiliations': ['CERN'],
            'creatorName': 'Doe, Jane',
            'familyName': 'Doe',
            'givenName': 'Jane',
            'nameIdentifiers': [
                {
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/',
                    'nameIdentifier': '0000-0002-1825-0097'
                }
            ],
        },
        {
            'affiliations': ['CERN'],
            'creatorName': 'Smith, John',
            'familyName': 'Smith',
            'givenName': 'John',
            'nameIdentifiers': [],
        },
        {
            'affiliations': ['CERN'],
            'creatorName': 'Nowak, Jack',
            'familyName': 'Nowak',
            'givenName': 'Jack',
            'nameIdentifiers': [
                {
                    'nameIdentifierScheme': 'GND',
                    'nameIdentifier': '170118215'
                }
            ],
        }
    ]

    expected['contributors'] = [
        {
            'affiliations': ['CERN'],
            'nameIdentifiers': [
                {
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/',
                    'nameIdentifier': '0000-0002-1825-0097'
                }
            ],
            'contributorName': 'Smith, Other',
            'familyName': 'Smith',
            'givenName': 'Other',
            'contributorType': 'Other',
        },
        {
            'affiliations': [''],
            'nameIdentifiers': [],
            'contributorName': 'Hansen, Viggo',
            'familyName': 'Hansen',
            'givenName': 'Viggo',
            'contributorType': 'Other',
        },
        {
            'affiliations': ['CERN'],
            'nameIdentifiers': [],
            'contributorName': 'Kowalski, Manager',
            'familyName': 'Kowalski',
            'givenName': 'Manager',
            'contributorType': 'DataManager',
        },
        {
            'contributorName': 'Smith, Professor',
            'familyName': 'Smith',
            'givenName': 'Professor',
            'nameIdentifiers': [],
            'contributorType': 'Supervisor',
        }
    ]
    expected['fundingReferences'] = []
    expected["dates"] = [
        {"date": "2014-02-27", "dateType": "Issued"},
        {"date": "2019-01-01/", "dateType": "Valid",
         "dateInformation": "Bongo"},
        {"date": "/2019-01-01", "dateType": "Collected"},
        {"date": "2019-01-01", "dateType": "Withdrawn"},
        {"date": "2019-01-01/2019-02-01", "dateType": "Collected"},
    ]
    expected['geoLocations'] = [{
        "geoLocationPlace": "my place",
        "geoLocationPoint": {
          "pointLatitude": 2.35,
          "pointLongitude": 1.534
        }
    }, {
        'geoLocationPlace': 'New York'
    }]
    assert obj == expected


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_identifier(db, minimal_record_model, recid_pid, serializer):
    """Test identifier."""
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['identifier'] == {
        'identifier': '10.5072/zenodo.123',
        'identifierType': 'DOI',
    }


def test_creators(db, minimal_record_model, recid_pid):
    """Test creators."""
    minimal_record_model.update({
        'creators': [
            {'name': 'A', 'affiliation': 'AA', 'gnd': '1234'},
            {'name': 'B', 'affiliation': 'BA', 'orcid': '0000-0000-0000-0000',
             'gnd': '4321'},
        ]})
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['creators'] == [
        {'affiliation': 'AA', 'creatorName': 'A', 'nameIdentifier': {
            'nameIdentifier': '1234', 'nameIdentifierScheme': 'GND'}},
        {'affiliation': 'BA', 'creatorName': 'B', 'nameIdentifier': {
            'nameIdentifier': '0000-0000-0000-0000',
            'nameIdentifierScheme': 'ORCID',
            'schemeURI': 'http://orcid.org/'}}
    ]


def test_creators_v4(db, minimal_record_model, recid_pid):
    """Test creators."""
    minimal_record_model.update({
        'creators': [
            {'name': 'A, B', 'affiliation': 'AA', 'gnd': '1234'},
            {
                'name': 'B',
                'affiliation': 'BA',
                'orcid': '0000-0000-0000-0000',
                'gnd': '4321'
            },
        ]})
    obj = datacite_v41.transform_record(recid_pid, minimal_record_model)
    assert obj['creators'] == [{
        'affiliations': ['AA'],
        'creatorName': 'A, B',
        'givenName': 'B',
        'familyName': 'A',
        'nameIdentifiers': [{
            'nameIdentifier': '1234',
            'nameIdentifierScheme': 'GND'
        }]},
        {
            'affiliations': ['BA'],
            'creatorName': 'B',
            'givenName': '',
            'familyName': '',
            'nameIdentifiers': [{
                'nameIdentifier': '0000-0000-0000-0000',
                'nameIdentifierScheme': 'ORCID',
                'schemeURI': 'http://orcid.org/'
            }, {
                'nameIdentifier': '4321',
                'nameIdentifierScheme': 'GND'
            }]
        }
    ]


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_embargo_date(db, minimal_record_model, recid_pid, serializer):
    """Test embargo date."""
    dt = (today() + timedelta(days=1)).isoformat()
    minimal_record_model.update({
        'embargo_date': dt,
        'access_right': 'embargoed',
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['dates'] == [
        {'dateType': 'Available', 'date': dt},
        {'dateType': 'Accepted', 'date': today().isoformat()},
    ]


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_subjects(db, minimal_record_model, recid_pid, serializer):
    """Test subjects date."""
    minimal_record_model.update({
        'keywords': ['kw1'],
        'subjects': [{'term': 'test', 'identifier': 'id', 'scheme': 'loc'}],
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['subjects'] == [
        {'subject': 'kw1'},
        {'subject': 'id', 'subjectScheme': 'loc'},
    ]


def test_contributors(db, minimal_record_model, recid_pid):
    """Test creators."""
    minimal_record_model.update({
        'contributors': [{
            'name': 'A',
            'affiliation': 'AA',
            'gnd': '1234',
            'type': 'Researcher'
        }, ],
        'thesis_supervisors': [{
            'name': 'B',
            'affiliation': 'BA',
            'type': 'Supervisor'
        }, ],
        'grants': [{
            'funder': {
                'name': 'European Commission',
            },
            'identifiers': {
                'eurepo': 'info:eu-repo/grantAgreement/EC/FP7/244909'
            },
        }],
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['contributors'] == [
        {
            'affiliation': 'AA',
            'contributorName': 'A',
            'contributorType': 'Researcher',
            'nameIdentifier': {
                'nameIdentifier': '1234',
                'nameIdentifierScheme': 'GND'}
        },
        {
            'affiliation': 'BA',
            'contributorName': 'B',
            'contributorType': 'Supervisor',
            'nameIdentifier': {},
        },
        {
            'contributorName': 'European Commission',
            'contributorType': 'Funder',
            'nameIdentifier': {
                'nameIdentifier': 'info:eu-repo/grantAgreement/EC/FP7/244909',
                'nameIdentifierScheme': 'info'}
        },
    ]


def test_contributors_v4(db, minimal_record_model, recid_pid):
    """Test contributors."""
    minimal_record_model.update({
        'contributors': [{
            'name': 'A, B',
            'affiliation': 'AA',
            'gnd': '1234',
            'orcid': '0000-0000-0000-0000',
            'type': 'Researcher'
        }, ],
        'thesis': {
            'supervisors': [{
                'name': 'B',
                'affiliation': 'BA',
                'type': 'Supervisor'
            }]
        }
    })
    obj = datacite_v41.transform_record(recid_pid, minimal_record_model)
    assert obj['contributors'] == [
        {
            'affiliations': ['AA'],
            'contributorName': 'A, B',
            'givenName': 'B',
            'familyName': 'A',
            'contributorType': 'Researcher',
            'nameIdentifiers': [
                {
                    'nameIdentifier': '0000-0000-0000-0000',
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/'
                },
                {
                    'nameIdentifier': '1234',
                    'nameIdentifierScheme': 'GND'
                },
            ]
        },
        {
            'affiliations': ['BA'],
            'contributorName': 'B',
            'givenName': '',
            'familyName': '',
            'contributorType': 'Supervisor',
            'nameIdentifiers': [],
        },
    ]

    # Test without `thesis` field
    minimal_record_model.pop('thesis', None)
    obj = datacite_v41.transform_record(recid_pid, minimal_record_model)
    assert obj['contributors'] == [
        {
            'affiliations': ['AA'],
            'contributorName': 'A, B',
            'givenName': 'B',
            'familyName': 'A',
            'contributorType': 'Researcher',
            'nameIdentifiers': [
                {
                    'nameIdentifier': '0000-0000-0000-0000',
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/'
                },
                {
                    'nameIdentifier': '1234',
                    'nameIdentifierScheme': 'GND'
                },
            ]
        },
    ]


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_language(db, minimal_record_model, recid_pid, serializer):
    """Test language."""
    assert 'language' not in minimal_record_model
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert 'language' not in obj

    minimal_record_model['language'] = 'eng'
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['language'] == 'en'  # DataCite supports ISO 639-1 (2-letter)

    minimal_record_model['language'] = 'twa'  # No ISO 639-1 code
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert 'language' not in obj

    # This should never happen, but in case of dirty data
    minimal_record_model['language'] = 'Esperanto'
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert 'language' not in obj


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_resource_type(db, minimal_record_model, recid_pid, serializer):
    """Test language."""
    minimal_record_model['resource_type'] = {'type': 'poster'}
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['resourceType'] == {
        'resourceTypeGeneral': 'Text',
        'resourceType': 'Poster',
    }

    # If the record is not in 'c1', OpenAIRE subtype should not be serialized
    minimal_record_model['resource_type'] = {'type': 'software',
                                             'openaire_subtype': 'foo:t1'}
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['resourceType'] == {
        'resourceTypeGeneral': 'Software',
        'resourceType': None
    }

    # Add 'c1' to communities. 'foo:t1' should be serialized as a type
    minimal_record_model['communities'] = ['c1', ]
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['resourceType'] == {
        'resourceTypeGeneral': 'Software',
        'resourceType': 'openaire:foo:t1',
    }


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_alt_ids(db, minimal_record_model, recid_pid, serializer):
    """Test language."""
    minimal_record_model.update({
        'alternate_identifiers': [{
            'identifier': '10.1234/foo.bar',
            'scheme': 'doi'
        }],
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['alternateIdentifiers'] == [{
        'alternateIdentifier': '10.1234/foo.bar',
        'alternateIdentifierType': 'doi',
    }, {
        'alternateIdentifier': 'http://localhost/record/123',
        'alternateIdentifierType': 'url',
    }]


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_related_identifiers(db, minimal_record_model, recid_pid, serializer):
    """Test language."""
    tests = [
        ('handle', 'Handle'),
        ('arxiv', 'arXiv'),
        ('ads', 'bibcode'),
        ('doi', 'DOI'),
    ]

    for t, dc_t in tests:
        minimal_record_model.update({
            'related_identifiers': [{
                'identifier': '1234',
                'scheme': t,
                'relation': 'isCitedBy',
                'resource_type': {
                    'type': 'publication',
                    'subtype': 'section'
                }
            }, {
                'identifier': '1234',
                'scheme': 'invalid',
                'relation': 'isCitedBy',
            }],
        })
        obj = serializer.transform_record(recid_pid, minimal_record_model)
        expected_result = [{
            'relatedIdentifier': '1234',
            'relatedIdentifierType': dc_t,
            'relationType': 'IsCitedBy',
            'resourceTypeGeneral': 'BookChapter'
        }]
        assert obj['relatedIdentifiers'] == expected_result


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_communities_rel_ids(db, minimal_record_model, recid_pid, serializer):
    """Test communities in related identifiers."""
    for communities in (['zenodo'], ['c1', 'c2', 'c3']):
        minimal_record_model['communities'] = communities
        obj = serializer.transform_record(recid_pid, minimal_record_model)
        for comm in communities:
            assert {
                'relatedIdentifier':
                    'http://localhost/communities/{}'.format(comm),
                'relatedIdentifierType': 'URL',
                'relationType': 'IsPartOf',
            } in obj['relatedIdentifiers']


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_rights(db, minimal_record_model, recid_pid, serializer):
    """Test language."""
    minimal_record_model.update({
        'license': {
            'identifier': 'cc-by-sa',
            'title': 'Creative Commons Attribution Share-Alike',
            'source': 'opendefinition.org',
            'url': 'http://www.opendefinition.org/licenses/cc-by-sa'
        }
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['rightsList'] == [{
        'rights': 'Creative Commons Attribution Share-Alike',
        'rightsURI': 'http://www.opendefinition.org/licenses/cc-by-sa',
    }, {
        'rights': 'Open Access',
        'rightsURI': 'info:eu-repo/semantics/openAccess',
    }]


@pytest.mark.parametrize("serializer", [
    datacite_v31,
    datacite_v41,
])
def test_descriptions(db, minimal_record_model, recid_pid, serializer):
    """Test descriptions."""
    minimal_record_model.update({
        'description': 'test',
        'notes': 'again',
        'references': [{'raw_reference': 'A'}],
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert obj['descriptions'] == [{
        'description': 'test',
        'descriptionType': 'Abstract',
    }, {
        'description': 'again',
        'descriptionType': 'Other',
    }, {
        'description': json.dumps({'references': ['A']}),
        'descriptionType': 'Other',
    }]

    minimal_record_model.update({
        'description': (20000 * 'A') + 'BBB',
        'notes': (20000 * 'A') + 'BBB',
        'references': [{'raw_reference': (20000 * 'A') + 'BBB'}],
    })
    obj = serializer.transform_record(recid_pid, minimal_record_model)
    assert all(len(d['description']) == 20000 and 'B' not in d['description']
               for d in obj['descriptions'])


def test_funding_ref_v4(db, minimal_record_model, recid_pid):
    """Test creators."""
    minimal_record_model.update({
        'grants': [
            {'title': 'Grant Title',
             'code': '1234',
             'identifiers': {'eurepo': 'eurepo 1'},
             'internal_id': '10.1234/foo::1234',
             'funder': {'name': 'EC', 'doi': '10.1234/foo'}},
            {'title': 'Title Grant',
             'code': '4321',
             'identifiers': {'eurepo': 'eurepo 2'},
             'internal_id': '10.1234/foo::4321',
             'funder': {'name': 'EC', 'doi': '10.1234/foo'}},
        ]})
    obj = datacite_v41.transform_record(recid_pid, minimal_record_model)
    assert obj['fundingReferences'] == [
        {
            'funderName': 'EC',
            'funderIdentifier': {
                'funderIdentifier': '10.1234/foo',
                'funderIdentifierType': 'Crossref Funder ID',
            },
            'awardNumber': {
                'awardNumber': '1234',
                'awardURI': 'eurepo 1'
            },
            'awardTitle': 'Grant Title'
        },
        {
            'funderName': 'EC',
            'funderIdentifier': {
                'funderIdentifier': '10.1234/foo',
                'funderIdentifierType': 'Crossref Funder ID',
            },
            'awardNumber': {
                'awardNumber': '4321',
                'awardURI': 'eurepo 2'
            },
            'awardTitle': 'Title Grant'
        }

    ]


def test_titles(db, minimal_record_model, recid_pid):
    """Test title."""
    # NOTE: There used to be a bug which was modifying the case of the title
    minimal_record_model['title'] = 'a lower-case title'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['titles'] == [{'title': 'a lower-case title'}]

    minimal_record_model['title'] = 'Mixed-caSe titLE'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['titles'] == [{'title': 'Mixed-caSe titLE'}]
