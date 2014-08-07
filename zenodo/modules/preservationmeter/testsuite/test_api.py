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

from mock import patch
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class CalculateScoreTest(InvenioTestCase):
    # @property
 #    def config(self):
 #        """Configuration property."""
 #        cfg = {
 #        }
 #        return cfg
    @patch('invenio.modules.records.api.get_record')
    def test_json_for_form(self, get_record_mock):
        from invenio.modules.records.api import Record
        # Patch return value of get_record()
        get_record_mock.return_value = Record(
            json={
                'doi': '10.1234/invenio.1234',
                'recid': 1,
            },
            master_format='marc'
        )

        # Now call get_record() which will return the value we've set above
        from invenio.modules.records.api import get_record
        r = get_record(1)
        assert r['doi'] == '10.1234/invenio.1234'

    def test_caculation(self):
        from zenodo.modules.preservationmeter.api import calculate_score
        score = calculate_score(8)
        print score
        assert score == 100


TEST_SUITE = make_test_suite(CalculateScoreTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
