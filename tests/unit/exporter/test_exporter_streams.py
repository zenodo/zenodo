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

"""Exporter stream tests."""

from __future__ import absolute_import, print_function

import bz2

import pytest

from zenodo.modules.exporter import BZip2ResultStream, ResultStream


@pytest.fixture()
def searchobj():
    """Search object"""
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
    """Serialize object"""
    class Serializer(object):
        def serialize_exporter(self, pid, record):
            return record['_source']['title'].encode('utf8')
    return Serializer()


@pytest.fixture()
def fetcher():
    """PID fetcher method"""
    def fetcher(id_, data):
        return id_
    return fetcher


@pytest.fixture()
def resultstream(searchobj, serializerobj, fetcher):
    """Result stream"""
    return ResultStream(searchobj, fetcher, serializerobj)


@pytest.fixture()
def bzip2resultstream(searchobj, serializerobj, fetcher):
    """BZip2 Result stream"""
    return BZip2ResultStream(searchobj, fetcher, serializerobj)


def test_resultstream(resultstream):
    """Test result stream serializer."""
    assert resultstream.read() == b'test 1'
    assert resultstream.read() == b'test 2'
    assert resultstream.read() == b''
    assert resultstream.read() == b''


def test_resultstream(bzip2resultstream):
    """Test result stream serializer."""
    c = bz2.BZ2Compressor()
    c.compress(b'test 1')
    c.compress(b'test 2')
    data = c.flush()

    assert bzip2resultstream.read() == data
    assert bzip2resultstream.read() == b''
