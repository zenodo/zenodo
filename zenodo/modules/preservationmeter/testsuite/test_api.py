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
from invenio.base.globals import cfg
from zenodo.modules.preservationmeter.api import calculate_score


class CalculateScoreTest(InvenioTestCase):

    @property
    def config(self):
        """Configuration property."""
        cfg = {  # Shouldn't do this like this?
            '.csv': 100,
            '.pdf': 100,
            '.txt': 95,
            '.odt': 95,
            '.xlsx': 60,
            '.docx': 60,
            '.xls': 40,
            '.doc': 40
        }
        cfg['files_var_name'] = '_files'
        return cfg

    @patch('invenio.modules.records.api.get_record')
    def test_record_mocking_files(self, get_record_mock):
        """Tests the general mocking of records.

        Namely, if the files of the record are accessible and
        also other general information.
        """
        # Patch return value of get_record()
        from invenio.modules.records.api import Record
        get_record_mock.return_value = Record(
            json={
                'doi': '10.1234/invenio.1234',
                'files_to_upload': [  # replace with cfg['files_var_name']
                    'path1.xls',
                    'path2.csv ',
                    'path3.pdf'],
                'recid': 1,
                # '_files': [  # replace with cfg['files_var_name']
                #    'path1',
                #    'path2',
                #    'path3']
            },
            master_format='marc'
        )

        # Now call get_record() which will return the value we've set above
        from invenio.modules.records.api import get_record
        r = get_record(1)
        assert r['doi'] == '10.1234/invenio.1234'
        assert r['files_to_upload'][0] == 'path1.xls'

        assert calculate_score([r['files_to_upload'][0]]) == 40

    @patch('invenio.modules.records.api.get_record')
    def test_get_extension(self, get_record_mock):
        from invenio.modules.records.api import Record
        get_record_mock.return_value = Record(
            json={
                'doi': '10.1234/invenio.1234',
                'files_to_upload': [
                    'path1.xls',
                    'path2.csv ',
                    'path3.pdf'],
                'recid': 1
            },
            master_format='marc'
        )
        from zenodo.modules.preservationmeter.api import get_file_extension
        from invenio.modules.records.api import get_record
        r = get_record(1)
        assert get_file_extension(r['files_to_upload'][0]) == '.xls'

    @patch('invenio.modules.records.api.get_record')
    def test_single_files(self, get_record_mock):
        """Test a with some basic document types

        Types:
         - csv
         - pdf
         - xlsx
         - txt
        """
        from invenio.modules.records.api import Record
        get_record_mock.return_value = Record(
            json={
                'doi': '10.1234/invenio.1234',
                'files_to_upload': [  # replace with cfg['files_var_name']
                    'path1.xls',
                    'path2.csv',
                    'path3.pdf'],
                'recid': 1,
                # '_files': [  # replace with cfg['files_var_name']
                #    'path1',
                #    'path2',
                #    'path3']
            },
            master_format='marc'
        )

        # Now call get_record() which will return the value we've set above
        from invenio.modules.records.api import get_record
        r = get_record(1)
        score = calculate_score(r['files_to_upload'])
        ####print score
        assert score == 80

    def test_docx_and_csv(self):
        assert True

    def test_csvs(self):
        assert True

    def test_zip_with_docx(self):
        assert True

    def test_tar_with_pdf(self):
        assert True

    def test_tar_with_apdf(self):
        assert True


TEST_SUITE = make_test_suite(CalculateScoreTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
