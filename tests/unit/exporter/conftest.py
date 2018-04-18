# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Exporter writers tests."""

from __future__ import absolute_import, print_function

import pytest
from flask import current_app
from invenio_files_rest.models import Bucket

from zenodo.modules.exporter import BucketWriter, BZip2ResultStream, \
    ResultStream


@pytest.fixture()
def exporter_bucket(db, locations):
    """Bucket to write in."""
    bucket_uuid = current_app.config['EXPORTER_BUCKET_UUID']
    return Bucket.create(id=bucket_uuid)


@pytest.fixture()
def writer(exporter_bucket):
    """Bucket writer object fixture."""
    return BucketWriter(bucket_id=exporter_bucket.id, key='test.json')


@pytest.fixture()
def searchobj():
    """Search object."""
    class Hit(dict):
        def __init__(self, *args, **kwargs):
            super(Hit, self).__init__(*args, **kwargs)

            class Meta(object):
                id = args[0]['id']

            self.meta = Meta()
            self._d_ = args[0]

    class Search(object):
        def scan(self):
            return iter([
                Hit({'id': 1, 'title': 'test 1'}),
                Hit({'id': 2, 'title': 'test 2'}),
            ])
    return Search()


@pytest.fixture()
def serializerobj():
    """Serialize object."""
    class Serializer(object):
        def serialize_exporter(self, pid, record):
            return record['_source']['title'].encode('utf8')
    return Serializer()


@pytest.fixture()
def fetcher():
    """PID fetcher method."""
    def fetcher(id_, data):
        return id_
    return fetcher


@pytest.fixture()
def resultstream(searchobj, serializerobj, fetcher):
    """Result stream."""
    return ResultStream(searchobj, fetcher, serializerobj)


@pytest.fixture()
def bzip2resultstream(searchobj, serializerobj, fetcher):
    """BZip2 Result stream."""
    return BZip2ResultStream(searchobj, fetcher, serializerobj)
