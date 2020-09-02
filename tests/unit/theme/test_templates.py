# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo template tests."""

from __future__ import absolute_import, print_function

import pytest
from helpers import login_user_via_session


def test_templates():
    """Test templates."""
    pass


@pytest.mark.parametrize('user_email,requests_num,status_code', [
    # anonymous user
    (None, 2, 429),
    # user
    ('test@zenodo.org', 4, 429),
])
def test_429_template(
    use_flask_limiter, app, app_client, db, users, user_email,
        requests_num, status_code, es):
    """Test flask limiter behaviour."""
    if user_email:
        # Login as user
        login_user_via_session(app_client, email=user_email)

    for x in range(0, requests_num):
        response = app_client.get('/search')
        assert response.status_code == 200

    response = app_client.get('/search')
    assert response.status_code == status_code

    response = app_client.get('/')
    assert response.status_code == 200

    if not user_email:
        response = app_client.get('/login')
        assert response.status_code == 200
