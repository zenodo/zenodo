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

"""Unit test for Zenodo json serializer."""

import json

import pytest
from flask import url_for
from helpers import login_user_via_session


@pytest.mark.parametrize('user_info, bucket_link, files', [
    # anonymous user
    (None, None, 0),
    # owner
    (dict(email='info@zenodo.org', password='tester'),
     'http://localhost/files/22222222-2222-2222-2222-222222222222', 1),
    # not owner
    (dict(email='test@zenodo.org', password='tester2'), None, 0),
    # admin user
    (dict(email='admin@zenodo.org', password='admin'),
     'http://localhost/files/22222222-2222-2222-2222-222222222222', 1),
])
def test_closed_access_record_serializer(api, users, json_headers,
                                         closed_access_record,
                                         user_info, bucket_link, files):
    """Test closed access record serialisation using records API."""
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])
            res = client.get(
                url_for('invenio_records_rest.recid_item',
                        pid_value=closed_access_record['recid']),
                headers=json_headers
            )
            r = json.loads(res.data.decode('utf-8'))
            assert r['links'].get('bucket', None) == bucket_link
            assert len(r.get('files', [])) == files


@pytest.mark.parametrize('user_info', [
    # anonymous user
    None,
    # owner
    dict(email='info@zenodo.org', password='tester'),
    # not owner
    dict(email='test@zenodo.org', password='tester2'),
    # admin user
    dict(email='admin@zenodo.org', password='admin'),
])
def test_closed_access_record_search_serializer(
        api, users, json_headers, user_info, closed_access_record):
    """Test closed access record serialisation of the search result."""
    with api.test_request_context():
        with api.test_client() as client:
            if user_info:
                # Login as user
                login_user_via_session(client, email=user_info['email'])
            res = client.get(
                url_for('invenio_records_rest.recid_list'),
                headers=json_headers
            )

            r = json.loads(res.data.decode('utf-8'))
            assert r[0]['links'].get('bucket', None) is None
            assert len(r[0].get('files', [])) == 0
