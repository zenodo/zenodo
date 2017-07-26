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

from flask import url_for
from invenio_accounts.models import User
from invenio_userprofiles.models import UserProfile


def test_orcid_profile_view(app, db, users):
    """Test Profile view for Non Zenodo User having orcid."""
    with app.test_client() as client:
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='YYYY-YYYY-YYYY-YYYY'))
        assert res.status_code == 404

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='XXXXXXXXXXXXXXXX'))
        assert res.status_code == 404

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='XXXX-XXXX-XXXX-XXX'))
        assert res.status_code == 404

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='XXXX-XXXX-XXX-XXXXX'))
        assert res.status_code == 404

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='XXXX-XXXX-XXXX-XXXX'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' in res.data

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='0000-0000-0000-0000'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' in res.data

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='1234-5678-9012-3456'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' in res.data


def test_user_profile_view(app, db, users):
    """Test Profile view for Zenodo User."""
    with app.test_client() as client:
        id = users[1]['id']
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 404

        user = User.query.get(id)
        user.profile = UserProfile(username='Testing')
        user.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 200
        assert b'Testing' in res.data

        user.researcher_profile.affiliation = 'Testing Organization'
        user.researcher_profile.location = 'Mock Island'
        user.researcher_profile.website = 'website@dont.exist'
        user.researcher_profile.bio = 'I am just testing profile page.'
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 200
        assert b'Testing' in res.data
        assert b'<small><br />Testing Organization</small>' in res.data
        assert b'<span>Mock Island</span>' in res.data
        assert b'website@dont.exist' in res.data
        assert b'<h3><small>I am just testing profile page.</small></h3>' \
            in res.data
        assert b'<button type="button" class="btn btn-default' \
            b' btn-lg btn-block">Contact</button>' not in res.data

        user.researcher_profile.allow_contact_owner = True
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 200
        assert b'<button type="button" class="btn btn-default' \
            b' btn-lg btn-block">Contact</button>' in res.data

        user.profile.full_name = 'Test User'
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 200
        assert b'Test User' in res.data
        assert b'<small><br />Testing</small>' in res.data

        user.researcher_profile.show_profile = False
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id))
        assert res.status_code == 404
