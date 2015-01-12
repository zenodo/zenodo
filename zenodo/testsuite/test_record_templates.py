# -*- coding: utf-8 -*-
#
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

from __future__ import print_function, absolute_import
import copy

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

from mock import patch, MagicMock, Mock
from flask import url_for
from bs4 import BeautifulSoup


class HeaderLinksTest(InvenioTestCase):
    @patch('invenio.legacy.bibdocfile.api.BibRecDocs')
    @patch('invenio.modules.records.views.get_record')
    def test_headerlinks_exists(self, get_record, BibRecDocs):
        """ Validate that link tags to files exists in document header. """
        # Patch up get record
        from zenodo.base.testsuite.test_jsonext import test_record
        record = copy.copy(test_record)
        get_record.return_value = record

        # Patch BibDocFile
        base_url = url_for('record.files', recid=1, _external=True)
        mock_file = MagicMock()
        mock_file.is_icon = Mock(return_value=False)
        mock_file.is_restricted = Mock(return_value=(False, False))
        mock_file.comment = "0"
        mock_file.mime = "application/pdf"
        mock_file.get_url = Mock(return_value=base_url+"test.pdf")
        mock_file.get_superformat = Mock(return_value=".pdf")
        BibRecDocs.return_value = MagicMock()
        BibRecDocs.return_value.list_latest_files = Mock(
            return_value=[mock_file])

        # Request page
        res = self.client.get(url_for('record.metadata', recid=3))
        self.assertEqual(res.status_code, 200)

        # Login to prevent errors fom
        soup = BeautifulSoup(res.data)
        for l in soup.select('link[rel="alternate"]'):
            if l['href'].startswith(base_url):
                return

        assert False, "<link> tags to files not found in record page."


TEST_SUITE = make_test_suite(HeaderLinksTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
