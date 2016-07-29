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

"""Test Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import json

from invenio_search import current_search
from six import BytesIO


def test_bucket_create_delete(api_client, deposit, json_auth_headers,
                              deposit_url, get_json, license_record,
                              auth_headers, minimal_deposit):
    """Test bucket created on deposit creation."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create deposit
    res = client.post(
        deposit_url, data=json.dumps(minimal_deposit), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Assert bucket was created and accessible
    assert 'bucket' in links
    res = client.get(links['bucket'], headers=auth)
    assert res.status_code == 200
    res = client.get(links['bucket'])
    assert res.status_code == 404

    # Upload object via files-rest.
    object_url = links['bucket'] + '/viafilesrest'
    res = client.put(
        object_url,
        input_stream=BytesIO(b'viafilesrest'),
        headers=auth,
    )
    assert res.status_code == 200

    # Get object via files-rest
    res = client.get(object_url, headers=auth)
    assert res.status_code == 200

    # List files in deposit.
    res = client.get(links['self'], headers=headers)
    data = get_json(res, code=200)
    assert len(data['files']) == 1

    # Get file via deposit.
    res = client.get(data['files'][0]['links']['self'], headers=headers)
    data = get_json(res, code=200)

    res = client.delete(links['self'], headers=auth)

    # Delete deposit
    assert res.status_code == 204

    # Assert bucket no longer exists
    res = client.get(links['bucket'], headers=auth)
    assert res.status_code == 404
    res = client.get(object_url, headers=auth)
    assert res.status_code == 404
