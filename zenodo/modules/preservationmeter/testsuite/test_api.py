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


from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class CalculateScoreTest(InvenioTestCase):
	# @property
 #    def config(self):
 #        """Configuration property."""
 #        cfg = {
           
 #        }
 #        return cfg
    

    def test_json_for_form(self):
    	from zenodo.modules.preservationmeter.api import calculate_score
    	calculate_score(1)


TEST_SUITE = make_test_suite(CalculateScoreTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
