# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""Simple script to make an upload via the REST API."""

from __future__ import absolute_import, print_function, unicode_literals

import json
from time import sleep

import requests
from six import BytesIO


def upload(token, metadata, files, publish=True):
    """Make an upload."""
    base_url = 'http://localhost:5000/api/deposit/depositions'
    auth = {
        'Authorization': 'Bearer {0}'.format(token)
    }
    auth_json = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    auth_json.update(auth)

    r = requests.post(base_url, data='{}', headers=auth_json)
    assert r.status_code == 201
    links = r.json()['links']
    print('Create deposit:')
    print(r.json())
    # Wait for ES to index.
    sleep(1)

    for filename, stream in files:
        r = requests.post(
            links['files'],
            data=dict(filename=filename),
            files=dict(file=stream),
            headers=auth)
        assert r.status_code == 201
        print('Upload file:')
        print(r.json())

    r = requests.put(
        links['self'],
        data=json.dumps(dict(metadata=metadata)),
        headers=auth_json
    )
    assert r.status_code == 200
    print('Update metadata:')
    print(r.json())

    if publish:
        r = requests.post(links['publish'], headers=auth)
        assert r.status_code == 202
        print('Publish:')
        print(r.json())

    return r.json()['id']


def upload_test(token, publish=True):
    """Test upload."""
    metadata = {
        'title': 'My first upload',
        'upload_type': 'publication',
        'publication_type': 'book',
        'description': 'This is my first upload',
        'access_right': 'open',
        'license': 'cc-by',
        'creators': [{'name': 'Doe, John', 'affiliation': 'Zenodo'}]
    }
    files = [('test.txt', BytesIO(b'My first test upload.'))]
    return upload(token, metadata, files, publish=publish)
