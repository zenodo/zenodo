# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from flask import url_for

from invenio.modules.oauthclient.testsuite.helpers import OAuth2ClientTestCase


class GitHubAuthenticationErrorsTest(OAuth2ClientTestCase):
    def test_bad_verification_code(self):
        # Test redirect
        resp = self.client.get(
            url_for("oauthclient.login", remote_app='github')
        )
        self.assertStatus(resp, 302)
        assert resp.location.startswith(
            "https://github.com/login/oauth/authorize"
        )

        # Mock up fake request from GitHub
        self.mock_response(app='github', data=dict(
            error_uri='http://developer.github.com/v3/oauth/'
                      '#bad-verification-code',
            error_description='The code passed is '
                              'incorrect or expired.',
            error='bad_verification_code',
        ))

        resp = self.client.get(
            url_for("oauthclient.authorized", remote_app='github', code='test')
        )

        # Assert that auth flow is reinitialized
        assert resp.status_code == 302
        assert resp.location.endswith(
            url_for('oauthclient.login', remote_app='github')
        )
