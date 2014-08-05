# -*- coding: utf-8 -*-
#
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

from __future__ import print_function, absolute_import
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

from flask import url_for
from bs4 import BeautifulSoup


class HeaderLinksTest(InvenioTestCase):
    def test_headerlinks_exists(self):
        """ Validate that link tags to files exists in document header. """
        from invenio.modules.records.models import Record
        latest_recid = Record.query.order_by(Record.id.desc()).first().id

        res = self.client.get(url_for('record.metadata', recid=latest_recid))

        soup = BeautifulSoup(res.data)
        base_url = url_for('record.files', recid=latest_recid, _external=True)

        for l in soup.select('link[rel="alternate"]'):
            if l['href'].startswith(base_url):
                return

        assert False, "<link> tags to files not found in record page."


TEST_SUITE = make_test_suite(HeaderLinksTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
