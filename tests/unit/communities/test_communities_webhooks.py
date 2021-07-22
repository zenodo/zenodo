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

import mock
import pytest
from flask import current_app
from helpers import publish_and_expunge

from zenodo.modules.communities.api import ZenodoCommunity


@pytest.fixture
def use_webhhoks_config(app):
    """Activate webhooks config."""
    old_value = current_app.config.pop('ZENODO_COMMUNITIES_WEBHOOKS', None)
    current_app.config['ZENODO_COMMUNITIES_WEBHOOKS'] = {
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
    yield
    current_app.config['ZENODO_COMMUNITIES_WEBHOOKS'] = old_value


def test_basic_webhooks(
        app, db, communities, deposit, deposit_file, use_webhhoks_config):
    """Test basic webhooks calls."""
    deposit['communities'] = ['c1']
    # On publish we're also creating the community inclusion request
    with mock.patch(
            'zenodo.modules.communities.tasks.requests.post') as requests_mock:
        published_deposit = publish_and_expunge(db, deposit)
        recid, record = published_deposit.fetch_published()
        calls = requests_mock.call_args_list
        assert len(calls) == 1
        call_args, call_kwargs = calls[0]
        assert call_kwargs['url'] == 'https://example.org/webhooks/zenodo'
        assert call_kwargs['headers'] == {
            'User-Agent': 'Zenodo v3.0.0',
            'X-Custom': 'custom-header',
        }
        assert call_kwargs['params'] == {
            'token': 'some-token'
        }
        assert call_kwargs['json']['event_type'] == \
            'community.records.inclusion'
        assert call_kwargs['json']['context'] == {
            'community': 'c1',
            'user': 1,

        }
        assert call_kwargs['json']['payload']['community'] == {
            'id': 'c1',
            'owner': {'id': 2},
        }

    with mock.patch(
            'zenodo.modules.communities.tasks.requests.post') as requests_mock:
        c1_api = ZenodoCommunity('c1')
        c1_api.accept_record(record, pid=recid)

        calls = requests_mock.call_args_list
        assert len(calls) == 1
        call_args, call_kwargs = calls[0]
        assert call_kwargs['url'] == 'https://example.org/webhooks/zenodo'
        assert call_kwargs['headers'] == {
            'User-Agent': 'Zenodo v3.0.0',
            'X-Custom': 'custom-header',
        }
        assert call_kwargs['params'] == {
            'token': 'some-token'
        }
        assert call_kwargs['json']['event_type'] == \
            'community.records.addition'
        assert call_kwargs['json']['context'] == {
            'community': 'c1',
            'user': 1,

        }
        assert call_kwargs['json']['payload']['community'] == {
            'id': 'c1',
            'owner': {'id': 2},
        }
