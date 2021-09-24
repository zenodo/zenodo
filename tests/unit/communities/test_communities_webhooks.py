# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2021 CERN.
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

"""Test Zenodo communities webhooks."""

from __future__ import absolute_import, print_function

import json

import mock
import pytest
from helpers import login_user_via_session
from six import BytesIO


@pytest.fixture
def use_webhooks_config(app, api):
    """Activate webhooks config."""
    old_value = app.config.pop('ZENODO_COMMUNITIES_WEBHOOKS', None)
    webhooks_config = {
        'c1': {
            'c1_recipient': {
                'url': 'https://example.org/webhooks/zenodo',
                'headers': {
                    'X-Custom': 'custom-header',
                },
                'params': {
                    'token': 'some-token'
                }
            },
        }
    }
    app.config['ZENODO_COMMUNITIES_WEBHOOKS'] = webhooks_config
    api.config['ZENODO_COMMUNITIES_WEBHOOKS'] = webhooks_config
    yield
    app.config['ZENODO_COMMUNITIES_WEBHOOKS'] = old_value
    api.config['ZENODO_COMMUNITIES_WEBHOOKS'] = old_value


def test_basic_webhooks(
        app, db, communities, deposit, deposit_file, mocker, es, deposit_url,
        get_json, json_auth_headers, license_record, users, app_client,
        api_client, use_webhooks_config):
    """Test community webhooks executions on inclusion request and approval."""
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
            access_right='open',
            license='CC0-1.0',
            communities=[{'identifier': 'c1'}],
        )
    )
    with mock.patch(
            'zenodo.modules.communities.tasks.requests.post') as requests_mock:
        res = api_client.post(
            deposit_url, data=json.dumps(test_data), headers=json_auth_headers)
        links = get_json(res, code=201)['links']
        recid = get_json(res, code=201)['id']
        deposit_bucket = links['bucket']
        deposit_edit = links['edit']
        deposit_publish = links['publish']

        # Upload files
        res = api_client.put(
            deposit_bucket + '/test1.txt',
            input_stream=BytesIO(b'testfile1'), headers=json_auth_headers)
        assert res.status_code == 200
        res = api_client.put(
            deposit_bucket + '/test2.txt',
            input_stream=BytesIO(b'testfile2'), headers=json_auth_headers)
        assert res.status_code == 200

        # Publish deposit
        res = api_client.post(deposit_publish, headers=json_auth_headers)
        links = get_json(res, code=202)['links']
        record_url = links['record']

        calls = requests_mock.call_args_list
        assert len(calls) == 1

        login_user_via_session(app_client, email=users[1]['email'])
        res = app_client.post(
            '/communities/c1/curaterecord/',
            json={'action': 'accept', 'recid': recid}
        )
        assert res.status_code == 200
        assert len(calls) == 2
