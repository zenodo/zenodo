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


"""OpenAIRE OAI-PMH client test suite."""

from __future__ import absolute_import

import httpretty

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

from ..contrib.openaire import clean_metadata
from .fixtures import FixtureMixin


class TestClient(InvenioTestCase, FixtureMixin):
    @httpretty.activate
    def test_client(self):
        c = self.get_client()
        grants = list(c.list_grants())
        self.assertEqual(len(grants), 200)
        self.assertEqual(
            grants[-1],
            {
                'end_date': u'2015-08-31',
                'title': u'The piRNA pathway in the Drosophila germline   a '
                         u'small RNA based genome immune system',
                'acronym': u'DROSOPIRNAS',
                'call_identifier': u'ERC-2010-StG_20091118',
                'ec_project_website': '',
                'grant_agreement_number': u'260711',
                'start_date': u'2010-09-01'}
        )

    def test_clean_metadata(self):
        output = clean_metadata(dict(
            value1=['test'],
            value0=[],
            valuelist=['test1', 'test2'],
        ))
        self.assertEqual(output, dict(
            value1='test',
            value0='',
            valuelist=['test1', 'test2'],
        ))


TEST_SUITE = make_test_suite(TestClient)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
