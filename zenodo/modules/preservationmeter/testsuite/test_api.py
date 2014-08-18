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


class RecordMock(object):

    """ Singleton RecordMocking used on several tests.

    Use to follow DRY principle.
    """

    record = None

    @staticmethod
    def get_mocked_record():
        from invenio.modules.records.api import Record
        if RecordMock.record is None:
            RecordMock.record = Record(
                json={
                    'doi': '10.1234/invenio.1234',
                    'files_to_upload': [  # replace with cfg['files_var_name']
                        'this/is/a/long/path/to/the/file/location/path1.xls',
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
        return RecordMock.record


class CalculateScoreTest(InvenioTestCase):

    def setUp(self):
        self.app.config

    @patch('invenio.modules.records.api.get_record')
    def test_record_mocking(self, get_record_mock):
        """Tests the general mocking of records.

        Namely, if the files of the record are accessible and
        also other general information.
        """
        ## First get the mockeed record
        r = RecordMock.get_mocked_record()
        ## Assert general information
        assert r['doi'] == '10.1234/invenio.1234'
        assert r['recid'] == 1

        ## Score calculation testing.
        ## For each file
        score1 = calculate_score([r['files_to_upload'][0]])
        score2 = calculate_score([r['files_to_upload'][1]])
        score3 = calculate_score([r['files_to_upload'][2]])
        assert score1 == 40
        assert score2 == 100
        assert score3 == 100
        ## And the average
        avg = (sum([score1, score2, score3])) / 3  # 80
        assert calculate_score(r['files_to_upload']) == avg

    @patch('invenio.modules.records.api.get_record')
    def test_get_extension(self, get_record_mock):
        """Tests the get_extension method from the API.
        """
        r = RecordMock.get_mocked_record()
        from zenodo.modules.preservationmeter.api import get_file_extension
        assert get_file_extension(r['files_to_upload'][0]) == '.xls'
        assert get_file_extension(r['files_to_upload'][1]) == '.csv'
        assert get_file_extension(r['files_to_upload'][2]) == '.pdf'
        assert get_file_extension('file/with/no/extension') == ''
        assert get_file_extension('file/with/no/name/.csv') == ''

    def test_single_files(self):
        """Test a with some basic document types

        Types:
         - csv
         - pdf
         - xlsx
        """
        r = RecordMock.get_mocked_record()
        score = calculate_score(r['files_to_upload'])
        assert score == 80

    """Tests concerning only the score calculation.

    No RecordMock needed, passing only file paths.
    """

    def test_docx_and_csv(self):
        """ CSV and DOCX should be 80
        """
        files = ['some/word_document.docx', 'and/a.csv']
        assert calculate_score(files) == 80

    def test_csvs(self):
        """Everything csv should be 100
        """
        files = ['something.csv', 'something-else.csv',
                 'and/also-this/thing.csv']
        assert calculate_score(files) == 100

    def test_tar_with_pdf(self):
        files = ['something.ble']
        assert calculate_score(files) == 0

    def test_unknown_extension(self):
        """Test if unknow or invalid extensions produce 0 score
        """
        files = ['something.ble', 'something']
        assert calculate_score(files) == 0

    def test_tar_with_apdf(self):
        """TODO
        """
        files = ['something.ble']
        assert calculate_score(files) == 0

    def test_zip_with_docx(self):
        """TODO
        """
        files = ['something.ble']
        assert calculate_score(files) == 0

TEST_SUITE = make_test_suite(CalculateScoreTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
