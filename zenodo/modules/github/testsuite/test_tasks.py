# -*- coding: utf-8 -*-
##
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import

import httpretty
import six

from invenio.celery.testsuite.helpers import CeleryTestCase
from invenio.ext.sqlalchemy import db
import json

from . import fixtures


class GitHubTestCase(CeleryTestCase):
    def setUp(self):
        # Create celery application
        self.create_celery_app()

        # Run Flask initialization code - to before_first_request functions
        # being executed
        with self.app.test_request_context(''):
            self.app.try_trigger_before_first_request_functions()
            self.app.preprocess_request()

        # Create a user
        from invenio.modules.accounts.models import User
        self.user = User(
            email='info@invenio-software.org', nickname='githubuser'
        )
        self.user.password = "githubuser"
        db.session.add(self.user)
        db.session.commit()

        # Create GitHub link
        from invenio.modules.oauthclient.models import RemoteToken
        from zenodo.modules.github.helpers import get_client_id
        from zenodo.modules.github.utils import init_account

        self.remote_token = RemoteToken.create(
            self.user.id,
            get_client_id(),
            "test",
            "",
        )

        # Init GitHub account and mock up GitHub API
        httpretty.enable()
        fixtures.register_github_api()
        init_account(self.remote_token)
        httpretty.disable()

    def tearDown(self):
        from invenio.modules.oauth2server.models import Token as ProviderToken

        # Disable httpretty if enabled
        httpretty.disable()
        httpretty.reset()

        # Destroy Celery application
        self.destroy_celery_app()

        # Remove GitHub token
        if self.remote_token:
            self.remote_token.remote_account.delete()

        # Remove User and provider tokens
        if self.user:
            ProviderToken.query.filter_by(user_id=self.user.id).delete()
            db.session.delete(self.user)

        db.session.commit()
        db.session.expunge_all()


class HandlePayloadTestCase(GitHubTestCase):
    def test_handle_payload(self):
        from zenodo.modules.github.tasks import handle_github_payload
        from invenio.modules.webhooks.models import Event

        httpretty.enable()
        extra_data = self.remote_token.remote_account.extra_data
        assert 'auser/repo-1' in extra_data['repos']
        assert 'auser/repo-2' in extra_data['repos']

        assert len(extra_data['repos']['auser/repo-1']['depositions']) == 0
        assert len(extra_data['repos']['auser/repo-2']['depositions']) == 0

        e = Event(
            user_id=self.user.id,
            payload=fixtures.PAYLOAD('auser', 'repo-1')
        )

        handle_github_payload.delay(e.__getstate__())

        assert len(extra_data['repos']['auser/repo-1']['depositions']) == 1
        assert len(extra_data['repos']['auser/repo-2']['depositions']) == 0

        dep = extra_data['repos']['auser/repo-1']['depositions'][0]

        assert dep['doi'].endswith(six.text_type(dep['record_id']))
        assert dep['errors'] is None
        assert dep['github_ref'] == "v1.0"


class PayloadExtractionTestCase(GitHubTestCase):
    def test_extract_files(self):
        from ..tasks import extract_files

        httpretty.enable()
        files = extract_files(
            fixtures.PAYLOAD('auser', 'repo-1', tag='v1.0')
        )
        assert len(files) == 1

        fileobj, filename = files[0]
        assert filename == "repo-1-v1.0.zip"

    def test_extract_metadata(self):
        from ..tasks import extract_metadata
        from ..helpers import get_api

        gh = get_api(user_id=self.user.id)

        # Mock up responses
        httpretty.enable()
        fixtures.register_endpoint(
            "/repos/auser/repo-2",
            fixtures.REPO('auser', 'repo-2'),
        )
        fixtures.register_endpoint(
            "/repos/auser/repo-2/contents/.zenodo.json",
            fixtures.CONTENT(
                'auser', 'repo-2', '.zenodo.json', 'v1.0',
                json.dumps(dict(
                    upload_type='dataset',
                    license='mit-license',
                    creators=[
                        dict(name='Smith, Joe', affiliation='CERN'),
                        dict(name='Smith, Joe', affiliation='CERN')
                    ]
                ))
            )
        )

        metadata = extract_metadata(
            gh,
            fixtures.PAYLOAD('auser', 'repo-2', tag='v1.0'),
        )

        assert metadata['upload_type'] == 'dataset'
