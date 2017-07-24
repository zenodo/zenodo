# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests Profiles."""

from __future__ import absolute_import, print_function


def test_orcid_profile_view(app, db):
    """Test Profile view for Non Zenodo User having orcid."""
    with app.test_client() as client:
        res = client.get("/profile")
        assert res.status_code == 404

        res = client.get("/profile/1000-0000-XXXX-XXXX")
        assert res.status_code == 404

        res = client.get("/profile/0000-0001-0000-0000")
        assert res.status_code == 200

        res = client.get("/profile/0000-0003-XXXX-XXXX")
        assert res.status_code == 200

        res = client.get('/profile/0000-0004-0000-0000')
        assert res.status_code == 404

        res = client.get('/profile/0000-0002-1825-0097')
        assert res.status_code == 200

        res = client.get('/profile/000-0002-1825-0097')
        assert res.status_code == 404

        res = client.get('/profile/0000000218250097')
        assert res.status_code == 404

        res = client.get('/profile/0000-0002-825-0097')
        assert res.status_code == 404

        res = client.get('/profile/0000-0002-825-0097-')
        assert res.status_code == 404

        res = client.get('/profile/0000-0002-825-009Y')
        assert res.status_code == 404

        res = client.get('/profile/0000-0002-825-00979')
        assert res.status_code == 404

        res = client.get('/profile/3')
        assert res.status_code == 404


# def test_user_profile_view(app, db, users):
#     """Test Profile view for Zenodo User."""
#     with app.test_client() as client:
#         user = users[1]
#         user.id = 1
#         user.researcher_profile.show_profile = True
#         res = client.get("/profile/1")
#         assert res.status_code == 200
