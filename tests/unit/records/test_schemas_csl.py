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

"""Zenodo CSL mapping test."""

from __future__ import absolute_import, print_function

from datetime import datetime

from invenio_records.api import Record

from zenodo.modules.records.serializers import csl_v1


def test_minimal(app, minimal_record, recid_pid):
    """Test minimal record."""
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    d = datetime.utcnow().date()
    assert obj == {
        'id': '123',
        'type': 'article',
        'title': 'Test',
        'abstract': 'My description',
        'author': [
            {'family': 'Test'},
        ],
        'issued': {
            'date-parts': [[d.year, d.month, d.day]]
        }
    }


def test_type(app, minimal_record, recid_pid):
    """"Test type."""
    minimal_record.update({
        'resource_type': {'type': 'publication', 'subtype': 'thesis'}
    })
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['type'] == 'thesis'

    minimal_record.update({
        'resource_type': {'type': 'publication'}
    })
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['type'] == 'article'

    minimal_record.update({
        'resource_type': {'type': 'image'}
    })
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['type'] == 'graphic'


def test_author(app, minimal_record, recid_pid):
    """"Test author."""
    minimal_record['creators'] = []
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['author'] == []

    minimal_record['creators'] = [
        {'familyname': 'TestFamily1', 'givennames': 'TestGiven1'},
        {'familyname': 'TestFamily2', 'name': 'TestName2'},
        {'name': 'TestName3'},
    ]
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['author'] == [
        {'family': 'TestFamily1', 'given': 'TestGiven1'},
        {'family': 'TestName2'},
        {'family': 'TestName3'},
    ]


def test_identifiers(app, minimal_record, recid_pid):
    """"Test identifiers."""
    minimal_record['doi'] = '10.1234/foo'
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['DOI'] == '10.1234/foo'
    assert 'publisher' not in obj

    minimal_record['doi'] = '10.5281/foo'
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['DOI'] == '10.5281/foo'
    assert obj['publisher'] == 'Zenodo'

    minimal_record['imprint'] = {'isbn': '978-1604598933'}
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['ISBN'] == '978-1604598933'

    minimal_record['alternate_identifiers'] = [{
        'identifier': 'ISSN 0264-2875',
        'scheme': 'issn'
    }]
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['ISSN'] == 'ISSN 0264-2875'


def test_journal(app, minimal_record, recid_pid):
    """Test journal record."""
    minimal_record['journal'] = {
        'volume': '42',
        'issue': '7',
        'title': 'Journal title',
        'pages': '10-20',
    }
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['container_title'] == 'Journal title'
    assert obj['volume'] == '42'
    assert obj['issue'] == '7'
    assert obj['page'] == '10-20'


def test_part_of(app, minimal_record, recid_pid):
    """Test journal record."""
    minimal_record['part_of'] = {
        'title': 'Conference proceedings title',
        'pages': '10-20',
    }
    minimal_record['imprint'] = {
        'publisher': 'The Good Publisher',
        'place': 'Somewhere',
    }
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['container_title'] == 'Conference proceedings title'
    assert obj['page'] == '10-20'
    assert obj['publisher'] == 'The Good Publisher'
    assert obj['publisher_place'] == 'Somewhere'


def test_other(app, minimal_record, recid_pid):
    """Test other fields."""
    minimal_record['language'] = 'en'
    minimal_record['notes'] = 'Test note'
    minimal_record['imprint'] = {
        'publisher': 'Zenodo',
    }
    obj = csl_v1.transform_record(recid_pid, Record(minimal_record))
    assert obj['language'] == 'en'
    assert obj['note'] == 'Test note'
    assert obj['publisher'] == 'Zenodo'
