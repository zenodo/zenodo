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

"""Test validation in Zenodo deposit REST API."""

from __future__ import absolute_import, print_function, unicode_literals

import json
from datetime import datetime

import jwt
from flask import url_for
from invenio_search import current_search
from six import BytesIO

from zenodo.modules.deposit.resolvers import deposit_resolver


def get_data(**kwargs):
    """Get test data."""
    test_data = dict(
        metadata=dict(
            upload_type='presentation',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
            ],
            description='Test Description',
            publication_date='2013-05-08',
            access_right='open'
        )
    )
    test_data['metadata'].update(kwargs)
    return test_data


def test_missing_files(api_client, json_auth_headers, deposit_url, locations,
                       es, get_json, license_record):
    """Test data validation - no files added."""
    client = api_client
    headers = json_auth_headers

    # Create
    res = client.post(
        deposit_url, data=json.dumps(get_data()), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Publish - not possible (file is missing)
    res = client.post(links['publish'], headers=headers)
    data = get_json(res, code=400)
    assert len(data['errors']) == 1


def test_multipart_onging(api, api_client, db, deposit, deposit_file, get_json,
                          json_auth_headers, deposit_url, license_record):
    """Test data validation."""
    api.config.update(dict(
        FILES_REST_MULTIPART_CHUNKSIZE_MIN=2,
    ))
    client = api_client
    headers = json_auth_headers
    deposit_url = '{0}/{1}'.format(
        deposit_url,
        deposit['_deposit']['id']
    )

    # Get links
    res = client.get(deposit_url, headers=headers)
    links = get_json(res, code=200)['links']

    # Create multipart upload
    multipart_url = '{0}/bigfile?uploads&size=1000&partSize=500'.format(
        links['bucket'])
    res = client.post(multipart_url, headers=headers)
    mp_links = get_json(res, code=200)['links']

    # Publish - not possible (multipart object in progress)
    res = client.post(links['publish'], headers=headers)
    data = get_json(res, code=400)
    assert len(data['errors']) == 1

    # Delete multipart upload
    assert client.delete(mp_links['self'], headers=headers).status_code == 204

    # Now publishing is possible
    assert client.post(links['publish'], headers=headers).status_code == 202


def test_file_ops(api_client, deposit, json_auth_headers, auth_headers,
                  deposit_url, get_json):
    """Test data validation."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create empty deposit
    res = client.post(deposit_url, data=json.dumps({}), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Upload same file twice - first ok, second not
    for code in [201, 400]:
        f = dict(file=(BytesIO(b'test'), 'test1.txt'), name='test1.txt')
        res = client.post(links['files'], data=f, headers=auth)
        res.status_code == code

    # Upload another file
    client.post(
        links['files'],
        data=dict(file=(BytesIO(b'test'), 'test2.txt'), name='test2.txt'),
        headers=auth
    )

    # List files
    data = get_json(client.get(links['files'], headers=headers), code=200)
    assert len(data) == 2
    file_id = data[0]['id']
    file_url = '{0}/{1}'.format(links['files'], file_id)

    # Get file
    assert client.get(file_url, headers=headers).status_code == 200

    # File does not exists
    assert client.get(
        '{0}/invalid'.format(links['files']), headers=headers
    ).status_code == 404

    data = get_json(client.get(links['files'], headers=headers), code=200)
    invalid_files_list = [dict(filename=x['filename']) for x in data]
    ok_files_list = list(reversed([dict(id=x['id']) for x in data]))

    # Sort - invalid
    assert client.put(
        links['files'], data=json.dumps(invalid_files_list), headers=headers
    ).status_code == 400

    # Sort - valid
    assert client.put(
        links['files'], data=json.dumps(ok_files_list), headers=headers
    ).status_code == 200

    # Delete
    assert client.delete(file_url, headers=headers).status_code == 204
    assert client.get(file_url, headers=headers).status_code == 404
    data = get_json(client.get(links['files'], headers=headers), code=200)
    assert len(data) == 1
    file_id = data[0]['id']
    file_url = '{0}/{1}'.format(links['files'], file_id)

    # Rename
    assert client.put(
        file_url, data=json.dumps(dict(filename='rename.txt')), headers=headers
    ).status_code == 200

    # Bad renaming
    for data in [dict(name='test.txt'), dict(filename='../../etc/passwd')]:
        assert client.put(
            file_url, data=json.dumps(data), headers=headers
        ).status_code == 400

    data = get_json(client.get(file_url, headers=headers), code=200)
    assert data['filename'] == 'rename.txt'


def test_deposit_deletion(api_client, deposit, json_auth_headers, deposit_url,
                          get_json, license_record, auth_headers):
    """Test file accessibility after deposit deletion."""
    client = api_client
    headers = json_auth_headers
    auth = auth_headers

    # Create
    res = client.post(
        deposit_url, data=json.dumps(get_data()), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Upload file
    res = client.post(
        links['files'],
        data=dict(file=(BytesIO(b'test'), 'test.txt'), name='test.txt'),
        headers=auth
    )
    assert res.status_code == 201

    # Get deposit links
    res = client.get(links['self'], headers=headers)
    data = get_json(res, code=200)
    file_link = data['files'][0]['links']['self']
    download_link = data['files'][0]['links']['download']

    # Get file
    res = client.get(file_link, headers=headers)
    assert res.status_code == 200
    res = client.get(download_link, headers=auth)
    assert res.status_code == 200

    # Get file - unauthenticated
    res = client.get(file_link)
    assert res.status_code == 401  # Any request requires auth.
    res = client.get(download_link)
    assert res.status_code == 404

    #
    # Delete upload
    #
    res = client.delete(links['self'], headers=auth)
    assert res.status_code == 204

    # Try to get deposit.
    res = client.get(links['self'], headers=auth)
    assert res.status_code == 410

    # Try to get file
    res = client.get(file_link, headers=headers)
    assert res.status_code == 410
    res = client.get(download_link, headers=auth)
    assert res.status_code == 404

    # Try to get file - unauthenticated
    res = client.get(file_link)
    assert res.status_code == 410
    res = client.get(download_link)
    assert res.status_code == 404


def test_rat_deposit_files_access(
        app, db, api_client, deposit, deposit_file, deposit_url,
        json_auth_headers, license_record, rat_generate_token):
    """Test deposit files access via RATs."""
    client = api_client
    depid = deposit['_deposit']['id']
    deposit['owners'] = [rat_generate_token.user_id]
    deposit['_deposit']['owners'] = [rat_generate_token.user_id]
    deposit.commit()
    db.session.commit()

    rat_token = jwt.encode(
        payload={
            'iat': datetime.utcnow(),
            'sub': {
                'deposit_id': depid,
                'access': 'read',
            },
        },
        key=rat_generate_token.access_token,
        algorithm='HS256',
        headers={'kid': str(rat_generate_token.id)},
    )

    deposit_url += '/' + str(depid)
    file_url = '/files/{}/test.txt'.format(deposit['_buckets']['deposit'])
    publish_url = deposit_url + '/actions/publish'

    res = client.get(file_url)
    assert res.status_code == 404

    res = client.get(file_url, query_string={'token': rat_token})
    assert res.status_code == 200

    # Try other forbidden operations using the RAT
    res = client.get(deposit_url, query_string={'token': rat_token})
    assert res.status_code == 401

    data = json.dumps(get_data())
    res = client.put(deposit_url, data=data, query_string={'token': rat_token})
    assert res.status_code == 401

    res = client.put(file_url, data=data, query_string={'token': rat_token})
    assert res.status_code == 404

    res = client.post(publish_url, query_string={'token': rat_token})
    assert res.status_code == 401

    # Change record owner
    depid, deposit = deposit_resolver.resolve(depid)
    deposit['owners'] = [123]
    deposit['_deposit']['owners'] = [123]
    deposit.commit()
    db.session.commit()

    res = client.get(file_url)
    assert res.status_code == 404
    res = client.get(file_url, query_string={'token': rat_token})
    assert res.status_code == 404
