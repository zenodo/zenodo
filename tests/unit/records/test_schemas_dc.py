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

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime, timedelta

from zenodo.modules.records.serializers import dc_v1


def test_minimal(app, db, minimal_record_model, recid_pid):
    """Test identifiers."""
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj == {
        'sources': [],
        'contributors': [],
        'identifiers': ['https://zenodo.org/record/123', '10.5072/zenodo.123'],
        'subjects': [],
        'languages': [''],
        'dates': [datetime.utcnow().date().isoformat()],
        'titles': ['Test'],
        'creators': ['Test'],
        'rights': ['info:eu-repo/semantics/openAccess'],
        'publishers': [],
        'descriptions': ['My description'],
        'types': [
            'info:eu-repo/semantics/other',
            'software',
        ],
        'relations': []
    }


def test_identifiers(app, db, minimal_record_model, recid_pid):
    """"Test identifiers."""
    minimal_record_model['doi'] = '10.1234/foo'
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['identifiers'] == \
        ['https://zenodo.org/record/123', '10.1234/foo']

    minimal_record_model['_oai'] = {'id': 'oai:zenodo.org:123'}
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert 'oai:zenodo.org:123' in obj['identifiers']


def test_creators(app, db, minimal_record_model, recid_pid):
    """"Test identifiers."""
    minimal_record_model['creators'] = []
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['creators'] == []


def test_languages(app, db, minimal_record_model, recid_pid):
    """"Test identifiers."""
    minimal_record_model['language'] = 'eng'
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['languages'] == ['eng', ]


def test_relations(app, db, minimal_record_model, recid_pid):
    """"Test relations."""
    minimal_record_model.update({
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
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['relations'] == [
        'info:eu-repo/grantAgreement/EC/FP7/244909',
        'info:eu-repo/semantics/altIdentifier/doi/10.1234/foo.bar',
        'pmid:1234'
    ]


def test_rights(app, db, minimal_record_model, recid_pid):
    """Test rights."""
    minimal_record_model.update({
        'license': {'url': 'http://creativecommons.org/licenses/by/4.0/'}
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert 'http://creativecommons.org/licenses/by/4.0/' in obj['rights']


def test_embargo_date(app, db, minimal_record_model, recid_pid):
    """"Test embargo date."""
    dt = (datetime.utcnow().date() + timedelta(days=1)).isoformat()
    minimal_record_model.update({
        'embargo_date': dt,
        'access_right': 'embargoed',
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['rights'] == ['info:eu-repo/semantics/embargoedAccess']
    assert 'info:eu-repo/date/embargoEnd/{0}'.format(dt) in obj['dates']


def test_publishers(app, db, minimal_record_model, recid_pid):
    """Test publishers."""
    minimal_record_model.update({
        'part_of': {'publisher': 'Zenodo'},
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['publishers'] == ['Zenodo']
    minimal_record_model.update({
        'imprint': {'publisher': 'Invenio'},
        'part_of': {'publisher': 'Zenodo'},
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['publishers'] == ['Invenio']


def test_contributors(app, db, minimal_record_model, recid_pid):
    """"Test contributors."""
    minimal_record_model.update({
        'contributors': [{'name': 'Smith, John'}]
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['contributors'] == ['Smith, John']


def test_types(app, db, minimal_record_model, recid_pid):
    """"Test contributors."""
    minimal_record_model.update({
        'resource_type': {'type': 'publication', 'subtype': 'conferencepaper'}
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['types'] == [
        'info:eu-repo/semantics/conferencePaper',
        'publication-conferencepaper'
    ]

    # If the record is not in 'c1', OpenAIRE subtype should not be serialized
    minimal_record_model.update({
        'resource_type': {'type': 'software',
                          'openaire_subtype': 'foo:t1'}
    })
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['types'] == [
        'info:eu-repo/semantics/other',
        'software'
    ]

    # Add 'c1' to communities. 'foo:t1' should be serialized as a type
    minimal_record_model.update({'communities': ['c1']})
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['types'] == [
        'info:eu-repo/semantics/other',
        'software',
        'openaire:foo:t1',
    ]


def test_community_relations(db, minimal_record_model, recid_pid):
    """Test communities."""
    for communities in (['zenodo'], ['c1', 'c2', 'c3']):
        minimal_record_model['communities'] = communities
        obj = dc_v1.transform_record(recid_pid, minimal_record_model)
        for comm in communities:
            assert ('url:http://localhost/communities/{}'.format(comm)
                    in obj['relations'])


def test_sources(app, db, minimal_record_model, recid_pid):
    """Test contributors."""
    minimal_record_model.update({
        'journal': {
            'title': 'CAP',
            'volume': '22',
            'issue': '1',
            'pages': '1-2',
            'year': '2002'
        }})
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['sources'] == ['CAP 22(1) 1-2 (2002)']

    minimal_record_model.update({
        'journal': {
            'title': 'CAP',
            'issue': '1',
        }})
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['sources'] == ['CAP 1']


def test_sources_meetings(app, db, minimal_record_model, recid_pid):
    """"Test contributors."""
    minimal_record_model['meetings'] = {
        'acronym': 'CAP',
        'title': 'Communicating',
        'place': 'Cape Town',
        'dates': 'March, 2010',
        'session': 'I',
        'session_part': '1',
    }
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['sources'] == ['CAP, Communicating, Cape Town, March, 2010']


def test_description(app, db, minimal_record_model, recid_pid):
    """Test description."""
    minimal_record_model['description'] = \
        "<p><b>Foo&nbsp;Bar</b></p><em><p>&nbsp;Foo&amp;Bar</p></em> &apos;" \
        "This&apos;&nbsp;is&nbsp;<i>&lt;it&gt;<i>"
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['descriptions'] == ["Foo Bar Foo&Bar 'This' is <it>"]

    minimal_record_model['description'] = ''
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['descriptions'] == []


def test_subjects(app, db, minimal_record_model, recid_pid):
    """Test description."""
    minimal_record_model['subjects'] = [{'term': 's1'}, {'term': 's2'}]
    minimal_record_model['keywords'] = ['k1', 'k2']
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert set(obj['subjects']) == {'s1', 's2', 'k1', 'k2'}


def test_dates(app, db, full_record, minimal_record_model, recid_pid):
    """Test dates."""
    minimal_record_model['dates'] = full_record['dates']
    obj = dc_v1.transform_record(recid_pid, minimal_record_model)
    assert obj['dates'] == [
        datetime.utcnow().date().isoformat(),
        '2019-01-01/',
        '/2019-01-01',
        '2019-01-01',
        '2019-01-01/2019-02-01',
    ]
