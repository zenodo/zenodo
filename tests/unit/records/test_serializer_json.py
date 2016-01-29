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

"""Zenodo serializer tests."""

from __future__ import absolute_import, print_function

import json

from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record
from marshmallow import Schema, fields

from zenodo.modules.records.serializers.json import JSONSerializer


def test_serialize():
    """Test JSON serialize."""
    class TestSchema(Schema):
        title = fields.Str(attribute='metadata.mytitle')
        id = fields.Str(attribute='pid.pid_value')

    data = json.loads(JSONSerializer(TestSchema).serialize(
        PersistentIdentifier(pid_type='recid', pid_value='2'),
        Record({'mytitle': 'test'})
    ))
    assert data['title'] == 'test'
    assert data['id'] == '2'


def test_serialize_search():
    """Test JSON serialize."""
    class TestSchema(Schema):
        title = fields.Str(attribute='metadata.mytitle')
        id = fields.Str(attribute='pid.pid_value')

    def fetcher(obj_uuid, data):
        assert obj_uuid in ['a', 'b']
        return PersistentIdentifier(pid_type='rec', pid_value=data['pid'])

    data = json.loads(JSONSerializer(TestSchema).serialize_search(
        fetcher,
        dict(
            hits=dict(
                hits=[
                    {'_source': dict(mytitle='test1', pid='1'), '_id': 'a',
                     '_version': 1},
                    {'_source': dict(mytitle='test2', pid='2'), '_id': 'b',
                     '_version': 1},
                ],
                total=2,
            ),
            aggregations={},
        )
    ))

    assert data['aggregations'] == {}
    assert 'links' in data
    assert data['hits'] == dict(
        hits=[
            dict(title='test1', id='1'),
            dict(title='test2', id='2'),
        ],
        total=2,
    )


def test_serialize_pretty(app):
    """Test pretty JSON."""
    class TestSchema(Schema):
        title = fields.Str(attribute='metadata.title')

    pid = PersistentIdentifier(pid_type='recid', pid_value='2'),
    rec = Record({'title': 'test'})

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    assert JSONSerializer(TestSchema).serialize(pid, rec) == \
        '{"title":"test"}'

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    assert JSONSerializer(TestSchema).serialize(pid, rec) == \
        '{\n  "title": "test"\n}'
