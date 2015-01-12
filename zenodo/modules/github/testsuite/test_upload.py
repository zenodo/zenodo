# -*- coding: utf-8 -*-
##
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
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

from functools import partial
from invenio.ext.sqlalchemy import db
from invenio.ext.restful.utils import APITestCase
from invenio.testsuite import make_pdf_fixture, make_test_suite, run_test_suite

from .helpers import tclient_request_factory


class ZenodoUploadTestCase(APITestCase):
    def setUp(self):
        from invenio.modules.accounts.models import User
        self.user = User(
            email='info@invenio-software.org', nickname='tester'
        )
        self.user.password = "tester"
        db.session.add(self.user)
        db.session.commit()
        self.create_oauth_token(
            self.user.id, scopes=["deposit:write", "deposit:actions"]
        )

    def tearDown(self):
        self.remove_oauth_token()
        if self.user:
            db.session.delete(self.user)
            db.session.commit()

    def test_upload(self):
        from ..upload import upload

        # Make request with test client instead of requests library
        factory = partial(tclient_request_factory, self.client)

        metadata = dict(
            upload_type="software",
            title="Test title",
            creators=[
                dict(name="Doe, John", affiliation="Atlantis"),
                dict(name="Smith, Jane", affiliation="Atlantis")
            ],
            description="Test Description",
            publication_date="2013-05-08",
        )
        files = [make_pdf_fixture('test.pdf', "upload test")]

        metadata = upload(
            self.accesstoken[self.user.id],
            metadata,
            files,
            publish=True,
            request_factory=factory
        )
        assert 'record_id' in metadata
        assert 'doi' in metadata


TEST_SUITE = make_test_suite(ZenodoUploadTestCase)


if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
