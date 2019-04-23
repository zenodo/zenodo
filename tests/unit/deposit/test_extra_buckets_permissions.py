# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

import pytest
from helpers import login_user_via_session

from zenodo.modules.deposit.resolvers import deposit_resolver


@pytest.mark.parametrize('user_email,status,use_scope', [
    # anonymous user
    (None, 403, False),
    # owner
    ('info@zenodo.org', 403, False),
    # owner with scope headers
    ('info@zenodo.org', 200, True),
    # not owner
    ('test@zenodo.org', 403, False),
    # admin user
    ('admin@zenodo.org', 200, False),
])
def test_extra_formats_permissions(
        api, api_client, db, users, deposit, extra_auth_headers,
        user_email, status, use_scope):
    if use_scope:
        user_headers = extra_auth_headers
    else:
        user_headers = []

    if user_email:
        # Login as user
        login_user_via_session(api_client, email=user_email)
    response = api_client.options(
        '/deposit/depositions/{0}/formats'.format(deposit['recid']),
        headers=user_headers)
    assert response.status_code == status


@pytest.mark.parametrize('user_email,status', [
    # anonymous user
    (None, 404),
    # owner
    ('info@zenodo.org', 404),
    # not owner
    ('test@zenodo.org', 404),
    # admin user
    ('admin@zenodo.org', 200),
])
def test_extra_formats_buckets_permissions(
        api, api_client, minimal_deposit, deposit_url, db, es, users,
        locations, json_extra_auth_headers, extra_auth_headers, license_record,
        user_email, status
        ):
    """Test Files-REST permissions for the extra formats bucket and files."""
    # Create deposit

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=json_extra_auth_headers)
    data = response.json

    # Get identifier and links
    depid = data['record_id']
    links = data['links']

    # Upload 1 files
    response = api_client.put(
        links['bucket'] + '/test1.txt',
        data='ctx',
        headers=extra_auth_headers,
    )

    # Add extra_formats bucket with a file
    response = api_client.put(
            '/deposit/depositions/{0}/formats'.format(depid),
            data='foo file',
            headers=[('Content-Type', 'application/foo+xml')] +
            extra_auth_headers
        )
    dep_uuid, deposit = deposit_resolver.resolve(depid)
    if user_email:
        # Login as user
        login_user_via_session(api_client, email=user_email)
    response = api_client.get(
        '/files/' + str(deposit.extra_formats.bucket.id)
    )
    assert response.status_code == status

    response = api_client.put(
        '/files/' + str(deposit.extra_formats.bucket.id) +
        '/application/foo+xml',
        data='ctx'
    )
    assert response.status_code == status

    # Publish deposition
    response = api_client.post(links['publish'], headers=extra_auth_headers)

    if user_email:
        # Login as user
        login_user_via_session(api_client, email=user_email)
    response = api_client.get(
        '/files/' + str(deposit.extra_formats.bucket.id)
    )
    assert response.status_code == status

    response = api_client.put(
        '/files/' + str(deposit.extra_formats.bucket.id) +
        '/application/foo+xml',
        data='ctx'
    )
    assert response.status_code == status
