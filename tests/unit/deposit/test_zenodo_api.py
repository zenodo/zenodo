# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import json

import pytest
from flask import url_for
from helpers import login_user_via_session
from invenio_search import current_search
from six import BytesIO


def get_json(response, code=None):
    """Decode JSON from response."""
    if code is not None:
        assert response.status_code == code
    return json.loads(response.get_data(as_text=True))


def make_file_fixture(filename, text=None):
    """Generate a PDF fixture."""
    content = text or filename.encode('utf8')
    return (BytesIO(content), filename)


def test_simple_rest_flow(api, api_client, db, es, location, users,
                          write_token):
    """Test simple flow using REST API."""
    client = api_client
    test_data = dict(
        metadata=dict(
            upload_type='presentation',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
                dict(name='Smith, Jane', affiliation='Atlantis')
            ],
            description='Test Description',
            publication_date='2013-05-08',
            access_right='open'
        )
    )

    # Prepare headers
    auth = write_token['auth_header']
    headers = [
        ('Content-Type', 'application/json'),
        ('Accept', 'application/json')
    ]
    auth_headers = headers + auth

    # Get deposit URL
    with api.test_request_context():
        deposit_url = url_for('invenio_deposit_rest.depid_list')

    # Try to create deposit as anonymous user (failing)
    response = client.post(
        deposit_url, data=json.dumps(test_data), headers=headers)
    assert response.status_code == 401

    # Create deposit
    response = client.post(
        deposit_url, data=json.dumps(test_data), headers=auth_headers)
    links = get_json(response, code=201)['links']

    # Get deposition
    current_search.flush_and_refresh(index='deposits')
    response = client.get(links['self'], headers=auth)
    assert response.status_code == 200

    # Upload 3 files
    for i in range(3):
        response = client.post(
            links['files'],
            data={
                'file': make_file_fixture('test{0}.txt'.format(i)),
                'name': 'test-{0}.txt'.format(i),
            },
            headers=auth,
        )
        assert response.status_code == 201, i

    # Publish deposition
    response = client.post(links['publish'], headers=auth_headers)
    record_id = get_json(response, code=202)['record_id']

    # Does record exists?
    current_search.flush_and_refresh(index='records')
    response = client.get(
        url_for('invenio_records_rest.recid_item', pid_value=record_id))

    # Second request will return forbidden since it's already published
    response = client.post(links['publish'], headers=auth_headers)
    assert response.status_code == 403  # FIXME should be 400

    # Not allowed to edit drafts
    response = client.put(
        links['self'], data=json.dumps(test_data), headers=auth_headers)
    assert response.status_code == 403

    # Not allowed to delete
    response = client.delete(
        links['self'], data=json.dumps(test_data), headers=auth)
    assert response.status_code == 403

    # Not allowed to sort files
    response = client.get(links['files'], headers=auth_headers)
    data = get_json(response, code=200)

    files_list = list(map(lambda x: {'id': x['id']}, data))
    files_list.reverse()
    response = client.put(
        links['files'], data=json.dumps(files_list), headers=auth)
    assert response.status_code == 403

    # Not allowed to add files
    i = 5
    response = client.post(
        links['files'],
        data={
            'file': make_file_fixture('test{0}.txt'.format(i)),
            'name': 'test-{0}.txt'.format(i),
        },
        headers=auth,
    )
    assert response.status_code == 403

    # Not allowed to delete file
    file_url = '{0}/{1}'.format(links['files'], files_list[0]['id'])
    response = client.delete(
        file_url, headers=auth)
    assert response.status_code == 403

    # Not allowed to rename file
    response = client.put(
        file_url,
        data=json.dumps(dict(filename='another_test.pdf')),
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # owner
    (dict(email='info@zenodo.org', password='tester'), 200),
    # not owner
    (dict(email='test@zenodo.org', password='tester2'), 403),
    # admin user
    (dict(email='admin@zenodo.org', password='admin'), 200),
])
def test_read_deposit_users(api, api_client, db, users, deposit, json_headers,
                            user_info, status):
    """Test read deposit by users."""
    deposit_id = deposit['_deposit']['id']
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])

            res = client.get(
                url_for('invenio_deposit_rest.depid_item',
                        pid_value=deposit_id),
                headers=json_headers
            )
            assert res.status_code == status


@pytest.mark.parametrize('user_info,status,count_deposit', [
    # anonymous user
    (None, 401, 0),
    # owner
    (dict(email='info@zenodo.org', password='tester'), 200, 1),
    # not owner
    (dict(email='test@zenodo.org', password='tester2'), 200, 0),
    # admin user
    (dict(email='admin@zenodo.org', password='admin'), 200, 1),
])
def test_read_deposits_users(api, api_client, db, users, deposit, json_headers,
                             user_info, status, count_deposit):
    """Test read deposit by users."""
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])

            res = client.get(
                url_for('invenio_deposit_rest.depid_list'),
                headers=json_headers
            )
            assert res.status_code == status
            if user_info:
                data = json.loads(res.data.decode('utf-8'))
                assert len(data) == count_deposit


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # owner
    (dict(email='info@zenodo.org', password='tester'), 200),
    # not owner
    (dict(email='test@zenodo.org', password='tester2'), 403),
    # admin user
    (dict(email='admin@zenodo.org', password='admin'), 200),
])
def test_update_deposits_users(api, api_client, db, users, deposit,
                               json_headers, user_info, status):
    """Test read deposit by users."""
    deposit_id = deposit['_deposit']['id']
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])

            res = client.put(
                url_for('invenio_deposit_rest.depid_item',
                        pid_value=deposit_id),
                data=json.dumps({}),
                headers=json_headers
            )
            assert res.status_code == status


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # owner
    (dict(email='info@zenodo.org', password='tester'), 204),
    # not owner
    (dict(email='test@zenodo.org', password='tester2'), 403),
    # admin user
    (dict(email='admin@zenodo.org', password='admin'), 204),
])
def test_delete_deposits_users(api, api_client, db, users, deposit,
                               json_headers, user_info, status):
    """Test read deposit by users."""
    deposit_id = deposit['_deposit']['id']
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])

            res = client.delete(
                url_for('invenio_deposit_rest.depid_item',
                        pid_value=deposit_id),
                headers=json_headers
            )
            assert res.status_code == status
