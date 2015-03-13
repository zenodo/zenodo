# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Test cases for login on Zenodo."""

from __future__ import absolute_import, print_function

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite


class LoginTestCase(InvenioTestCase):

    """Test related to account access.

    Test requires that demo fixtures have been loaded and not tampered with.
    """

    def test_blocked_login(self):
        """Test if blocked account can login."""
        self.assertStatus(self.login("blocked", "blocked"), 401)

    def test_inactive_login(self):
        """Test if inactive account can login."""
        self.assertStatus(self.login("inactive", "inactive"), 200)

    def test_active_login(self):
        """Test if normal account can login."""
        self.assertStatus(self.login("usera", "usera"), 200)


class UnconfirmedEmailTestCase(InvenioTestCase):

    """Test related to message to users that their email is unconfirmed."""

    def test_inactive_login(self):
        """Test if blocked account can login."""
        response = self.login("inactive", "inactive")
        self.assertStatus(response, 200)
        assert 'You have not yet verified your email address.' in response.data
        response = self.client.get('/account/settings/profile/')
        assert 'Send verification email' in response.data

    def test_active_login(self):
        """Test if blocked account can login."""
        response = self.login("usera", "usera")
        self.assertStatus(response, 200)
        assert 'You have not yet verified your email address.' not in \
            response.data
        response = self.client.get('/account/settings/profile/')
        assert 'Send verification email' not in response.data


TEST_SUITE = make_test_suite(LoginTestCase, UnconfirmedEmailTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
