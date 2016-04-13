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

from datetime import date, timedelta

from invenio_records.api import Record

from zenodo.modules.records.serializers import dc_v1


def test_minimal(minimal_record, recid_pid):
    """Test identifiers."""
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj == {
        'sources': [],
        'contributors': [],
        'identifiers': ['', 'https://zenodo.org/record/123'],
        'subjects': [],
        'languages': [''],
        'dates': [date.today().isoformat()],
        'titles': ['Test'],
        'creators': ['Test'],
        'rights': ['info:eu-repo/semantics/openAccess'],
        'publishers': [],
        'descriptions': ['My description'],
        'types': ['info:eu-repo/semantics/other'],
        'relations': []
    }


def test_identifiers(minimal_record, recid_pid):
    """"Test identifiers."""
    minimal_record['doi'] = '10.1234/foo'
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['identifiers'] == \
        ['10.1234/foo', 'https://zenodo.org/record/123']

    minimal_record['_oai'] = {'id': 'oai:zenodo.org:123'}
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert 'oai:zenodo.org:123' in obj['identifiers']


def test_creators(minimal_record, recid_pid):
    """"Test identifiers."""
    minimal_record['creators'] = []
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['creators'] == []


def test_relations(minimal_record, recid_pid):
    """"Test relations."""
    minimal_record.update({
        'grants': [{
            'identifiers': {
                'eurepo': 'info:eu-repo/grantAgreement/EC/FP7/244909'}}],
        'alternate_identifiers': [{
            'identifier': '10.1234/foo.bar',
            'scheme': 'doi'
        }],
        'related_identifiers': [{
            'identifier': '1234',
            'scheme': 'pmid',
            'relation': 'isCited',
        }],
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['relations'] == [
        'info:eu-repo/grantAgreement/EC/FP7/244909',
        'info:eu-repo/semantics/altIdentifier/doi/10.1234/foo.bar',
        'pmid:1234'
    ]


def test_rights(minimal_record, recid_pid):
    """Test rights."""
    minimal_record.update({
        'license': {'url': 'http://creativecommons.org/licenses/by/4.0/'}
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert 'http://creativecommons.org/licenses/by/4.0/' in obj['rights']


def test_embargo_date(minimal_record, recid_pid):
    """"Test embargo date."""
    dt = (date.today() + timedelta(days=1)).isoformat()
    minimal_record.update({
        'embargo_date': dt,
        'access_right': 'embargoed',
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['rights'] == ['info:eu-repo/semantics/embargoedAccess']
    assert 'info:eu-repo/date/embargoEnd/{0}'.format(dt) in obj['dates']


def test_publishers(minimal_record, recid_pid):
    """Test publishers."""
    minimal_record.update({
        'part_of': {'publisher': 'Zenodo'},
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['publishers'] == ['Zenodo']
    minimal_record.update({
        'imprint': {'publisher': 'Invenio'},
        'part_of': {'publisher': 'Zenodo'},
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['publishers'] == ['Invenio']


def test_contributors(minimal_record, recid_pid):
    """"Test contributors."""
    minimal_record.update({
        'contributors': [{'name': 'Smith, John'}]
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['contributors'] == ['Smith, John']


def test_types(minimal_record, recid_pid):
    """"Test contributors."""
    minimal_record.update({
        'resource_type': {'type': 'publication', 'subtype': 'conferencepaper'}
    })
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['types'] == ['info:eu-repo/semantics/conferencePaper']


def test_sources(minimal_record, recid_pid):
    """"Test contributors."""
    minimal_record.update({
        'journal': {
            'title': 'CAP',
            'volume': '22',
            'issue': '1',
            'pages': '1-2',
            'year': '2002'
        }})
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['sources'] == ['CAP 22(1) 1-2 (2002)']

    minimal_record.update({
        'journal': {
            'title': 'CAP',
            'issue': '1',
        }})
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['sources'] == ['CAP 1']


def test_sources_meetings(minimal_record, recid_pid):
    """"Test contributors."""
    minimal_record['meetings'] = {
        'acronym': 'CAP',
        'title': 'Communicating',
        'place': 'Cape Town',
        'dates': 'March, 2010',
        'session': 'I',
        'session_part': '1',
    }
    obj = dc_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['sources'] == ['CAP, Communicating, Cape Town, March, 2010']
