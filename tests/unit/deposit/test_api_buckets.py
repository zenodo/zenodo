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
    """Test bucket creation/deletion of bucket with each deposit."""
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

    # Delete deposit
    res = client.delete(links['self'], headers=auth)
    assert res.status_code == 204

    # Assert bucket no longer exists
    res = client.get(links['bucket'], headers=auth)
    assert res.status_code == 404
    res = client.get(object_url, headers=auth)
    assert res.status_code == 404


def test_bucket_create_publish(api_client, deposit, json_auth_headers,
                               deposit_url, get_json, license_record,
                               auth_headers, minimal_deposit):
    """Test bucket features on deposit publish."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create deposit
    res = client.post(
        deposit_url, data=json.dumps(minimal_deposit), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Upload file
    res = client.put(
        links['bucket'] + '/test.txt',
        input_stream=BytesIO(b'testfile'),
        headers=auth,
    )
    assert res.status_code == 200

    # Publish deposit
    res = client.post(links['publish'], headers=auth)
    data = get_json(res, code=202)

    # Bucket should be locked.
    res = client.put(
        links['bucket'] + '/newfile.txt',
        input_stream=BytesIO(b'testfile'),
        headers=auth,
    )
    assert res.status_code == 403

    # Get deposit.
    res = client.get(links['self'], headers=auth)
    assert res.status_code == 200

    # Get record.
    res = client.get(data['links']['record'])
    data = get_json(res, code=200)

    # Assert record and deposit bucket is not identical.
    assert data['links']['bucket'] != links['bucket']

    # Get record bucket.
    res = client.get(data['links']['bucket'])
    assert res.status_code == 200

    # Get file in bucket.
    res = client.get(data['links']['bucket'] + '/test.txt')
    assert res.status_code == 200

    # Record bucket is also locked.
    res = client.put(
        data['links']['bucket'] + '/newfile.txt',
        input_stream=BytesIO(b'testfile'),
        headers=auth,
    )
    assert res.status_code == 404

    # Delete deposit not allowed
    res = client.delete(links['self'], headers=auth)
    assert res.status_code == 403


def test_bucket_new_version(api_client, deposit, json_auth_headers,
                            deposit_url, get_json, license_record,
                            auth_headers, minimal_deposit):
    """Test bucket features on record new version."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create deposit
    res = client.post(
        deposit_url, data=json.dumps(minimal_deposit), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Upload file
    res = client.put(
        links['bucket'] + '/test.txt',
        input_stream=BytesIO(b'testfile'),
        headers=auth,
    )
    assert res.status_code == 200

    # Publish deposit
    res = client.post(links['publish'], headers=auth)
    data = get_json(res, code=202)

    # Get record
    res = client.get(data['links']['record'])
    data = get_json(res, code=200)
    rec_v1_bucket = data['links']['bucket']

    # Get deposit
    res = client.get(links['self'], headers=auth)
    links = get_json(res, code=200)['links']
    dep_v1_bucket = links['bucket']

    # Create new version
    res = client.post(links['newversion'], headers=auth)
    data = get_json(res, code=201)

    # Get new version deposit
    res = client.get(data['links']['latest_draft'], headers=auth)
    data = get_json(res, code=200)
    dep_v2_publish = data['links']['publish']
    dep_v2_bucket = data['links']['bucket']

    # Assert that all the buckets are different
    assert len(set([rec_v1_bucket, dep_v1_bucket, dep_v2_bucket])) == 3

    # Get file from old version deposit bucket
    res = client.get(dep_v1_bucket + '/test.txt', headers=auth)
    dep_v1_file_data = res.get_data(as_text=True)

    # Get file from old version record bucket
    res = client.get(rec_v1_bucket + '/test.txt')
    rec_v1_file_data = res.get_data(as_text=True)

    # Get file from new version deposit bucket
    res = client.get(dep_v2_bucket + '/test.txt', headers=auth)
    dep_v2_file_data = res.get_data(as_text=True)

    # Assert that the file is the same in the new version
    assert rec_v1_file_data == dep_v1_file_data == dep_v2_file_data

    # Record bucket is unlocked.
    res = client.put(
        dep_v2_bucket + '/newfile.txt',
        input_stream=BytesIO(b'testfile2'),
        headers=auth,
    )
    assert res.status_code == 200

    # Deleting files in new version deposit bucket is allowed
    res = client.delete(dep_v2_bucket + '/newfile.txt', headers=auth)
    assert res.status_code == 204

    # Publish new version deposit
    res = client.post(dep_v2_publish, headers=auth)
    data = get_json(res, code=202)

    # Get record
    res = client.get(data['links']['record'])
    data = get_json(res, code=200)
    rec_v2_bucket = data['links']['bucket']

    # Assert that all the buckets are different
    assert len(set(
        [rec_v1_bucket, rec_v2_bucket, dep_v1_bucket, dep_v2_bucket])) == 4
