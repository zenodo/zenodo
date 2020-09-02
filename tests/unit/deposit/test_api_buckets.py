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
                            auth_headers, minimal_deposit, indexer_queue):
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

    # Try to publish the new version
    # Should fail (400), since the bucket contents is the same
    res = client.post(dep_v2_publish, headers=auth)
    data = get_json(res, code=400)

    # Add another file, so that the bucket has a different content
    res = client.put(
        dep_v2_bucket + '/newfile2.txt',
        input_stream=BytesIO(b'testfile3'),
        headers=auth,
    )
    assert res.status_code == 200

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

    # Create another new version
    res = client.post(links['newversion'], headers=auth)
    data = get_json(res, code=201)

    # Get new version deposit
    res = client.get(data['links']['latest_draft'], headers=auth)
    data = get_json(res, code=200)

    dep_v3_bucket = data['links']['bucket']
    dep_v3_publish = data['links']['publish']

    # Try to publish the new version without changes (should fail as before)
    res = client.post(dep_v3_publish, headers=auth)
    data = get_json(res, code=400)

    # Deleting the file from v2 should be possible, but publishing should
    # also fail since the contents will be the same as the very first version.
    res = client.delete(dep_v3_bucket + '/newfile2.txt', headers=auth)
    assert res.status_code == 204

    res = client.post(dep_v3_publish, headers=auth)
    data = get_json(res, code=400)


def test_non_zenodo_doi(api_client, deposit, json_auth_headers,
                        deposit_url, get_json, license_record,
                        auth_headers, minimal_deposit, indexer_queue):
    """Test non-Zenodo DOI bucket operations."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create non-Zenodo DOI deposit
    minimal_deposit['metadata']['doi'] = '10.1234/nonzenodo'
    res = client.post(
        deposit_url, data=json.dumps(minimal_deposit), headers=headers)
    links = get_json(res, code=201)['links']
    deposit_bucket = links['bucket']
    deposit_edit = links['edit']
    deposit_publish = links['publish']

    # Upload files
    res = client.put(
        deposit_bucket + '/test1.txt',
        input_stream=BytesIO(b'testfile1'), headers=auth)
    assert res.status_code == 200
    res = client.put(
        deposit_bucket + '/test2.txt',
        input_stream=BytesIO(b'testfile2'), headers=auth)
    assert res.status_code == 200

    # Publish deposit
    res = client.post(deposit_publish, headers=auth)
    links = get_json(res, code=202)['links']
    record_url = links['record']

    # Deposit bucket shouldn't be editable
    res = client.put(
        deposit_bucket + '/test3.txt',
        input_stream=BytesIO(b'testfile3'), headers=auth)
    assert res.status_code == 403

    # Get record
    res = client.get(record_url)
    record_bucket = get_json(res, code=200)['links']['bucket']

    # Record bucket shouldn't be editable either
    res = client.put(
        record_bucket + '/test3.txt',
        input_stream=BytesIO(b'testfile3'), headers=auth)
    assert res.status_code == 404

    # Keep the record files around for later comparison
    res = client.get(record_bucket, headers=auth)
    record_files_initial = {
        (f['key'], f['checksum']) for f in get_json(res, code=200)['contents']}

    # Edit the deposit
    res = client.post(deposit_edit, headers=auth)
    assert res.status_code == 201

    # Deposit bucket now should be editable to add files...
    res = client.put(
        deposit_bucket + '/test3.txt',
        input_stream=BytesIO(b'testfile3'), headers=auth)
    assert res.status_code == 200

    # ...remove files...
    res = client.delete(deposit_bucket + '/test1.txt', headers=auth)
    assert res.status_code == 204

    # ...and edit files.
    res = client.put(
        deposit_bucket + '/test2.txt',
        input_stream=BytesIO(b'testfile3_modifed'), headers=auth)
    assert res.status_code == 200

    # While editing the deposit, record files should be the same
    res = client.get(record_bucket, headers=auth)
    record_files = {
        (f['key'], f['checksum']) for f in get_json(res, code=200)['contents']}
    assert record_files == record_files_initial

    # Publish deposit with changed files
    res = client.post(deposit_publish, headers=auth)
    assert res.status_code == 202

    # Deposit bucket should be closed again
    res = client.put(
        deposit_bucket + '/test4.txt',
        input_stream=BytesIO(b'testfile4'), headers=auth)
    assert res.status_code == 403

    # Check that record files were updated
    res = client.get(deposit_bucket, headers=auth)
    deposit_files = {
        (f['key'], f['checksum']) for f in get_json(res, code=200)['contents']}
    res = client.get(record_bucket, headers=auth)
    record_files = {
        (f['key'], f['checksum']) for f in get_json(res, code=200)['contents']}

    assert deposit_files == record_files
    assert record_files != record_files_initial
