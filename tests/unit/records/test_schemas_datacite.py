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

"""Zenodo Dublin Core mapping test."""

from __future__ import absolute_import, print_function

import json
from datetime import datetime, timedelta

from zenodo.modules.records.serializers import datacite_v31


def today():
    """Get todays UTC date."""
    return datetime.utcnow().date()


def test_minimal(db, minimal_record_model, recid_pid):
    """Test minimal."""
    minimal_record_model['doi'] = '10.1234/foo'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj == {
        'identifier': {'identifier': '10.1234/foo', 'identifierType': 'DOI'},
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


def test_identifier(db, minimal_record_model, recid_pid):
    """Test identifier."""
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert 'identifier' not in obj


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


def test_embargo_date(db, minimal_record_model, recid_pid):
    """Test embargo date."""
    dt = (today() + timedelta(days=1)).isoformat()
    minimal_record_model.update({
        'embargo_date': dt,
        'access_right': 'embargoed',
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['dates'] == [
        {'dateType': 'Available', 'date': dt},
        {'dateType': 'Accepted', 'date': today().isoformat()},
    ]


def test_subjects(db, minimal_record_model, recid_pid):
    """Test subjects date."""
    minimal_record_model.update({
        'keywords': ['kw1'],
        'subjects': [{'term': 'test', 'identifier': 'id', 'scheme': 'loc'}],
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
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


def test_language(db, minimal_record_model, recid_pid):
    """Test language."""
    minimal_record_model['language'] = 'eng'
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['language'] == 'eng'


def test_resource_type(db, minimal_record_model, recid_pid):
    """Test language."""
    minimal_record_model['resource_type'] = {'type': 'poster'}
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['resourceType'] == {
        'resourceTypeGeneral': 'Text',
        'resourceType': 'Poster',
    }


def test_alt_ids(db, minimal_record_model, recid_pid):
    """Test language."""
    minimal_record_model.update({
        'alternate_identifiers': [{
            'identifier': '10.1234/foo.bar',
            'scheme': 'doi'
        }],
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['alternateIdentifiers'] == [{
        'alternateIdentifier': '10.1234/foo.bar',
        'alternateIdentifierType': 'doi',
    }, {
        'alternateIdentifier': 'http://localhost/record/123',
        'alternateIdentifierType': 'url',
    }]


def test_related_identifiers(db, minimal_record_model, recid_pid):
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
            }, {
                'identifier': '1234',
                'scheme': 'invalid',
                'relation': 'isCitedBy',
            }],
        })
        obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
        assert obj['relatedIdentifiers'] == [{
            'relatedIdentifier': '1234',
            'relatedIdentifierType': dc_t,
            'relationType': 'IsCitedBy',
        }]


def test_rights(db, minimal_record_model, recid_pid):
    """Test language."""
    minimal_record_model.update({
        'license': {
            'identifier': 'cc-by-sa',
            'title': 'Creative Commons Attribution Share-Alike',
            'source': 'opendefinition.org',
            'url': 'http://www.opendefinition.org/licenses/cc-by-sa'
        }
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
    assert obj['rightsList'] == [{
        'rights': 'Creative Commons Attribution Share-Alike',
        'rightsURI': 'http://www.opendefinition.org/licenses/cc-by-sa',
    }, {
        'rights': 'Open Access',
        'rightsURI': 'info:eu-repo/semantics/openAccess',
    }]


def test_descriptions(db, minimal_record_model, recid_pid):
    """Test language."""
    minimal_record_model.update({
        'description': 'test',
        'notes': 'again',
        'references': [{'raw_reference': 'A'}],
    })
    obj = datacite_v31.transform_record(recid_pid, minimal_record_model)
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
