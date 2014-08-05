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

from __future__ import absolute_import

from mock import patch
from invenio.testsuite import make_test_suite, run_test_suite
from invenio.celery.testsuite.helpers import CeleryTestCase

from ..config import PRESERVATIONMETER_FILES_FIELD


class CalculateScoreTaskTest(CeleryTestCase):

    @patch('zenodo.modules.preservationmeter.tasks.get_record')
    @patch('invenio.legacy.bibupload.utils.bibupload_record')
    def test_task(self, bibupload_record, get_record):
        get_record.return_value = {
            'recid': 1,
            PRESERVATIONMETER_FILES_FIELD: [
                dict(path='path/to/content.pdf;1', full_name='test.pdf')
            ]
        }

        bibupload_record.return_value = True

        from zenodo.modules.preservationmeter.tasks import \
            calculate_preservation_score

        calculate_preservation_score.delay(recid=1)
        assert get_record.called
        self.assertEqual(
            '<record>\n    <controlfield tag="001">1</controlfield>\n    <datafield tag="347" ind1="" ind2="">\n        <subfield code="p">100</subfield>\n    </datafield>\n    </record>\n    ',
            bibupload_record.call_args[0][0],
        )

TEST_SUITE = make_test_suite(CalculateScoreTaskTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
