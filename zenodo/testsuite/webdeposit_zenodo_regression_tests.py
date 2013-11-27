# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
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

from invenio.config import CFG_SITE_SECURE_URL
from invenio.testutils import make_test_suite, run_test_suite, \
    InvenioTestCase, make_pdf_fixture
import json


class WebDepositZenodoTest(InvenioTestCase):
    #
    # Tests
    #
    def test_identical_filenames(self):
        from flask import url_for, current_app

        with current_app.test_client() as c:
            # Login
            c.post(
                url_for('webaccount.login'),
                base_url=CFG_SITE_SECURE_URL,
                data=dict(nickname="admin", password=""),
                follow_redirects=True
            )

            # Create deposition
            response = c.post(
                url_for('webdeposit.create'),
                headers=[('X-Requested-With', 'XMLHttpRequest')],
                base_url=CFG_SITE_SECURE_URL
            )
            self.assert200(response)
            uuid = response.data

            # Upload file
            f = make_pdf_fixture("identicalname.pdf")
            response = c.post(
                url_for('webdeposit.upload_file', uuid=uuid),
                data=dict(file=f),
                headers=[('X-Requested-With', 'XMLHttpRequest')],
                base_url=CFG_SITE_SECURE_URL
            )
            self.assert200(response)

            # Second file with identical name fails
            f = make_pdf_fixture("identicalname.pdf")
            response = c.post(
                url_for('webdeposit.upload_file', uuid=uuid),
                data=dict(file=f),
                headers=[('X-Requested-With', 'XMLHttpRequest')],
                base_url=CFG_SITE_SECURE_URL
            )
            self.assert400(response)

            # Delete it again
            response = c.get(
                url_for('webdeposit.delete', uuid=uuid),
                headers=[('X-Requested-With', 'XMLHttpRequest')],
                base_url=CFG_SITE_SECURE_URL
            )
            self.assert_status(response, 302)


            # # Run workflow
            # response = c.get(
            #     url_for('webdeposit.run', uuid=uuid),
            #     base_url=CFG_SITE_SECURE_URL
            # )

            # # Update data
            # response = c.post(
            #     url_for('webdeposit.save', uuid=uuid,
            #             draft_id="_default", all="1"),
            #     base_url=CFG_SITE_SECURE_URL,
            #     headers=[('X-Requested-With', 'XMLHttpRequest')],
            #     content_type='application/json',
            #     data=json.dumps({
            #         "publication_date": "2013-10-30",
            #         "title": "Test",
            #         "creators": [
            #             {"name": "Doe, John", "affiliation": "Atlantis"}
            #         ],
            #         "description": "Test",
            #         "access_right": "open",
            #         "license": "cc-zero",
            #     })
            # )
            # self.assert200(response)

            # # Submit
            # response = c.post(
            #     url_for('webdeposit.save', uuid=uuid, draft_id="_default",
            #             submit="1"),
            #     base_url=CFG_SITE_SECURE_URL,
            #     headers=[('X-Requested-With', 'XMLHttpRequest')],
            # )
            # self.assert200(response)

            # # Run workflow
            # response = c.get(
            #     url_for('webdeposit.run', uuid=uuid),
            #     base_url=CFG_SITE_SECURE_URL
            # )
            # self.assert200(response)


TEST_SUITE = make_test_suite(WebDepositZenodoTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
