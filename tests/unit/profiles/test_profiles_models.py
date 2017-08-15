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

"""Tests for researcher profile models."""

from __future__ import absolute_import, print_function

from invenio_accounts.models import User

from zenodo.modules.profiles import Profile


def test_profiles(app):
    """Test Profile model."""
    researcher_profile = Profile()

    assert researcher_profile.show_profile is None
    assert researcher_profile.allow_contact_owner is None
    assert researcher_profile.bio is None
    assert researcher_profile.affiliation is None
    assert researcher_profile.location is None
    assert researcher_profile.website is None
    researcher_profile.show_profile = True
    researcher_profile.allow_contact_owner = True
    researcher_profile.bio = 'Tester bio'
    researcher_profile.affiliation = 'Testing world'
    researcher_profile.location = 'Testing land'
    researcher_profile.website = 'Tester.testing'
    assert researcher_profile.show_profile
    assert researcher_profile.allow_contact_owner
    assert researcher_profile.bio == 'Tester bio'
    assert researcher_profile.affiliation == 'Testing world'
    assert researcher_profile.location == 'Testing land'
    assert researcher_profile.website == 'Tester.testing'


def test_profile_updating(app, db):
    """Test Profile model update."""
    with app.app_context():
        user = User(email='lollorosso', password='test_password')
        db.session.add(user)
        db.session.commit()

        assert user.researcher_profile is not None

        researcher_profile = Profile.get_by_userid(user.id)

        researcher_profile.affiliation = 'Testing world'
        researcher_profile.location = 'Testing land'
        assert researcher_profile.affiliation == 'Testing world'
        assert researcher_profile.location == 'Testing land'


def test_delete_cascade(app, db):
    """Test that deletion of user, also removes profile."""
    with app.app_context():
        with db.session.begin_nested():
            user = User(email='test@example.org')
            db.session.add(user)
        db.session.commit()

        assert Profile.get_by_userid(user.id) is not None
        db.session.delete(user)
        db.session.commit()

        assert Profile.get_by_userid(user.id) is None
