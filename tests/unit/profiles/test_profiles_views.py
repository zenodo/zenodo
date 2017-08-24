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

import pytest

from flask import url_for
from helpers import login_user_via_session
from invenio_accounts.models import User
from invenio_userprofiles.models import UserProfile
from werkzeug import MultiDict


@pytest.mark.parametrize('orcid, status', [
    ('YYYY-YYYY-YYYY-YYYY', 404),
    ('XXXXXXXXXXXXXXXX', 404),
    ('XXXX-XXXX-XXXX-XXX', 404),
    ('XXXX-XXXX-XXX-XXXXX', 404),
    ('XXXX-XXXX-XXXX-XXXX', 200),
    ('0000-0000-0000-0000', 200),
    ('1234-5678-9012-3456', 200),
])
def test_orcid_profile_endpoint(app, db, es, orcid, status):
    """Test Profile endpoint for Non Zenodo User having orcid."""
    with app.test_client() as client:
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id=orcid))
        assert res.status_code == status


def test_orcid_profile_view(app, db, es, users, orcid_user, record_indexer):
    """Test Profile view for Non Zenodo User having orcid."""
    with app.test_client() as client:
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' in res.data
        assert b'Testing' not in res.data

        user = User.query.get(users[1]['id'])
        user.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' in res.data
        assert b'Testing' not in res.data

        user.profile = UserProfile(username='Testing')
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' not in res.data
        assert b'Testing' in res.data
        assert b'<button type="button" class="btn btn-default btn-lg' \
            b' btn-block">Contact</button>' not in res.data

        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='0000-0002-1694-233X'))
        assert res.status_code == 200
        assert b'Test title' in res.data
        assert b'Test Description' in res.data

        user.researcher_profile.allow_contact_owner = True
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' not in res.data
        assert b'<button type="button" class="btn btn-default btn-lg' \
            b' btn-block">Contact</button>' in res.data

        login_user_via_session(client, email=users[1]['email'])
        res = client.get(url_for('zenodo_profiles.profile',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'<div id="orcid_profile">' not in res.data
        assert b'<button type="button" class="btn btn-default btn-lg' \
            b' btn-block">Contact</button>' not in res.data


def test_user_profile_view(app, db, es, users, orcid_user, record_indexer):
    """Test Profile view for Zenodo User."""
    with app.test_client() as client:
        id1 = users[1]['id']
        id2 = users[0]['id']

        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 404

        user1 = User.query.get(id1)
        user1.profile = UserProfile(username='Testing')
        user1.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 200
        assert b'Testing' in res.data

        user1.researcher_profile.affiliation = 'Testing Organization'
        user1.researcher_profile.location = 'Mock Island'
        user1.researcher_profile.website = 'website@dont.exist'
        user1.researcher_profile.bio = 'I am just testing profile page.'
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 200
        assert b'Testing' in res.data
        assert b'<small><br />Testing Organization</small>' in res.data
        assert b'<span>Mock Island</span>' in res.data
        assert b'website@dont.exist' in res.data
        assert b'<h3><small>I am just testing profile page.</small></h3>' \
            in res.data
        assert b'<button type="button" class="btn btn-default' \
            b' btn-lg btn-block">Contact</button>' not in res.data

        user1.researcher_profile.allow_contact_owner = True
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 200
        assert b'<button type="button" class="btn btn-default' \
            b' btn-lg btn-block">Contact</button>' in res.data

        user1.profile.full_name = 'Test User'
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 200
        assert b'Test User' in res.data
        assert b'<small><br />Testing</small>' in res.data

        user1.researcher_profile.show_profile = False
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id1))
        assert res.status_code == 404

        user2 = User.query.get(id2)
        user2.profile = UserProfile(username='Testing_orcid')
        user2.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile', owner_id=id2))
        assert res.status_code == 200
        assert b'Test title' in res.data
        assert b'Test Description' in res.data


def test_user_profile_search_view(app, db, users):
    """Test Profile search view for Zenodo user."""
    with app.test_client() as client:
        id = users[1]['id']

        res = client.get(url_for('zenodo_profiles.profile_search',
                                 owner_id=id))
        assert res.status_code == 404

        user = User.query.get(id)
        user.profile = UserProfile(username='Testing')
        res = client.get(url_for('zenodo_profiles.profile_search',
                                 owner_id=id))
        assert res.status_code == 404

        user.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile_search',
                                 owner_id=id))
        assert res.status_code == 200
        assert b'Testing' in res.data


def test_orcid_profile_search_view(app, db, orcid_user, users):
    """Test Profile search view for orcid user."""
    with app.test_client() as client:
        user = User.query.get(users[1]['id'])

        res = client.get(url_for('zenodo_profiles.profile_search',
                                 orcid_id='XXXX-XXXX-XXXX-XXXX'))
        assert res.status_code == 200

        user.researcher_profile.show_profile = True
        res = client.get(url_for('zenodo_profiles.profile_search',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'Testing' not in res.data

        user.profile = UserProfile(username='Testing')
        res = client.get(url_for('zenodo_profiles.profile_search',
                                 orcid_id='X123-4567-890X-1234'))
        assert res.status_code == 200
        assert b'Testing' in res.data


def test_profile_contact_view(app, db, users):
    """Test Profile contact form."""
    with app.extensions['mail'].record_messages() as outbox:
        with app.test_client() as client:
            res = client.get(url_for('zenodo_profiles.profile_contact',
                                     owner_id=users[1]['id']))
            assert res.status_code == 302

            login_user_via_session(client, email=users[0]['email'])
            res = client.get(url_for('zenodo_profiles.profile_contact',
                                     owner_id=users[1]['id']))
            assert res.status_code == 404

            user = User.query.get(users[1]['id'])
            user.profile = UserProfile(username='Testing')
            user.researcher_profile.show_profile = True
            res = client.get(url_for('zenodo_profiles.profile_contact',
                                     owner_id=users[1]['id']))
            assert res.status_code == 404

            user.researcher_profile.allow_contact_owner = True
            res = client.get(url_for('zenodo_profiles.profile_contact',
                                     owner_id=users[1]['id']))
            assert res.status_code == 200
            assert b'Testing' in res.data

            res = client.post(
                url_for('zenodo_profiles.profile_contact',
                        owner_id=users[1]['id']),
                data=dict()
            )
            assert res.status_code == 200
            assert b'error-name' in res.data
            assert b'error-subject' in res.data
            assert b'error-body' in res.data

            form = MultiDict(dict(
                name='Aman',
                subject='hello',
                body='Please help us! Troubleshoot our problem.'
            ))
            res = client.post(
                url_for('zenodo_profiles.profile_contact',
                        owner_id=users[1]['id']),
                data=form
            )
            assert b'has-error' not in res.data
            assert len(outbox) == 1
            sent_msg = outbox[0]
            assert sent_msg.sender == app.config[
                'ZENODO_PROFILES_SENDER_EMAIL']
            assert sent_msg.subject == 'hello'
            assert sent_msg.reply_to == users[0]['email']
            assert 'Please help us! Troubleshoot our problem.' in sent_msg.body
            assert 'Aman ' in sent_msg.body
            assert users[0]['email'] in sent_msg.body
