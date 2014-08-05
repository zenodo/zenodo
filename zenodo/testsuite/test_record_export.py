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


class RecordExportTest(InvenioTestCase):
    def test_hidden_tags(self):
        """ Validate that link tags to files exists in document header. """
        from invenio.modules.records.models import Record

        TEST_FORMATS = ['hm', 'xm']
        latest_recid = Record.query.order_by(Record.id.desc()).first().id

        for fmt in TEST_FORMATS:
            res = self.client.get(
                url_for('record.metadata', recid=latest_recid, of=fmt)
            )
            if fmt == 'hm':
                self.assertTrue('8560_f' not in res.data)
            elif fmt == 'xm':
                self.assertTrue('tag="856" ind1="0" ind2=" "'
                                not in res.data)


TEST_SUITE = make_test_suite(RecordExportTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
