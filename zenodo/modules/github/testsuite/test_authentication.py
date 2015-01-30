# -*- coding: utf-8 -*-
##
## This file is part of Zenodo.
## Copyright (C) 2014, 2015 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import

from flask import url_for
from mock import MagicMock
import httpretty
from urlparse import parse_qs, urlparse

from invenio.testsuite import make_test_suite, run_test_suite
from invenio.ext.sqlalchemy import db
from invenio.modules.oauthclient.testsuite.helpers import OAuth2ClientTestCase

from . import fixtures


class GitHubAuthenticationErrorsTest(OAuth2ClientTestCase):
    @classmethod
    def get_state(cls, url):
        return parse_qs(urlparse(url).query)['state'][0]

    @property
    def config(self):
        return dict(
            # HTTPretty doesn't play well with Redis.
            # See gabrielfalcao/HTTPretty#110
            CACHE_TYPE='simple',
            OAUTH2_CACHE_TYPE='simple',
        )

    def setUp(self):
        super(GitHubAuthenticationErrorsTest, self).setUp()

        from invenio.modules.oauthclient.models import RemoteToken, \
            RemoteAccount
        from invenio.modules.accounts.models import User

        RemoteToken.query.delete()
        RemoteAccount.query.delete()
        db.session.commit()
        db.session.expunge_all()

        User.query.filter_by(email='noemailuser@invenio-software.org').delete()

    def test_bad_verification_code(self):
        # Test redirect
        resp = self.client.get(
            url_for("oauthclient.login", remote_app='github')
        )
        self.assertStatus(resp, 302)
        assert resp.location.startswith(
            "https://github.com/login/oauth/authorize"
        )
        state = self.get_state(resp.location)

        httpretty.enable()
        fixtures.register_github_api()

        # Test restart of auth flow when getting a bad_verification_code
        resp = self.client.get(
            url_for(
                "oauthclient.authorized",
                remote_app='github',
                code='bad_verification_code',
                state=state,
            )
        )

        assert resp.status_code == 302
        assert resp.location.endswith(
            url_for('oauthclient.login', remote_app='github')
        )

        httpretty.disable()
        httpretty.reset()

    def test_no_public_email(self):
        # Test redirect
        resp = self.client.get(
            url_for("oauthclient.login", remote_app='github', next='/mytest/')
        )
        self.assertStatus(resp, 302)
        assert resp.location.startswith(
            "https://github.com/login/oauth/authorize"
        )
        state = self.get_state(resp.location)

        httpretty.enable()
        fixtures.register_oauth_flow()
        fixtures.register_endpoint(
            "/user",
            fixtures.USER('noemailuser', bio=False)
        )

        # Assert user is redirect to page requesting email address
        resp = self.client.get(
            url_for(
                "oauthclient.authorized",
                remote_app='github',
                code='test_no_email',
                state=state,
            )
        )
        self.assertRedirects(
            resp,
            url_for("oauthclient.signup", remote_app='github', )
        )

        # Mock account setup to prevent GitHub queries
        from invenio.modules.oauthclient.client import signup_handlers
        signup_handlers['github']['setup'] = MagicMock()

        resp = self.client.post(
            url_for(
                "oauthclient.signup",
                remote_app='github',
            ),
            data={'email': 'noemailuser@invenio-software.org'}
        )
        self.assertRedirects(
            resp,
            '/mytest/',
        )

        from invenio.modules.accounts.models import User
        assert User.query.filter_by(
            email='noemailuser@invenio-software.org').count() == 1

        httpretty.disable()
        httpretty.reset()


TEST_SUITE = make_test_suite(GitHubAuthenticationErrorsTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
