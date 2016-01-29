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

import uuid

from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import Record
from datetime import datetime

from zenodo.modules.records.serializers.base import PreprocessorMixin

keys = ['pid', 'metadata', 'links', 'revision', 'created', 'updated']


def test_preprocessor_mixin_record(app, db):
    """Test preprocessor mixin."""
    with db.session.begin_nested():
        recuuid = uuid.uuid4()
        record = Record.create({'title': 'test'}, id_=recuuid)
        record.model.created = datetime(2015, 10, 1, 11, 11, 11, 1)
        pid = PersistentIdentifier.create(
            'recid', '1', object_type='rec', object_uuid=recuuid,
            status=PIDStatus.REGISTERED)
    db.session.commit()

    data = PreprocessorMixin.preprocess_record(pid, record)
    for k in keys:
        assert k in data

    assert data['metadata']['title'] == 'test'
    assert data['created'] == '2015-10-01T11:11:11.000001+00:00'
    assert data['revision'] == 1

    data = PreprocessorMixin.preprocess_record(pid, Record({'title': 'test2'}))
    assert data['created'] is None
    assert data['updated'] is None


def test_preprocessor_mixin_searchhit():
    """Test preprocessor mixin."""
    pid = PersistentIdentifier(
        pid_type='doi', pid_value='10.1234/foo', status='R')

    data = PreprocessorMixin.preprocess_search_hit(pid, {
        '_source': {
            'title': 'test',
            '_created': '2015-10-01T11:11:11.000001+00:00',
            '_updated': '2015-12-01T11:11:11.000001+00:00',
        },
        '_version': 1,
    })

    for k in keys:
        assert k in data

    assert data['metadata']['title'] == 'test'
    assert data['created'] == '2015-10-01T11:11:11.000001+00:00'
    assert data['revision'] == 1
    assert '_created' not in data['metadata']
    assert '_updated' not in data['metadata']

    data = PreprocessorMixin.preprocess_search_hit(pid, {
        '_source': {'title': 'test'},
        '_version': 1,
    })
    assert data['created'] is None
    assert data['updated'] is None
