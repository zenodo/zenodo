## -*- coding: utf-8 -*-
##
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

from mock import patch
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
import zenodo.modules.preservationmeter.api as api
import tempfile
import os.path as osp
from shutil import rmtree
try:
    from shutil import make_archive
except ImportError:
    from .python26 import make_archive


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
                        ('path1.xls', 'this/is/a/long/path/to/the/file/location/path1.xls'),
                        ('path2.csv', 'path2.csv'),
                        ('path3.pdf', 'path3.pdf'), ],
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
        # First get the mockeed record
        r = RecordMock.get_mocked_record()
        # Assert general information
        self.assertEqual(r['doi'], '10.1234/invenio.1234')
        self.assertEqual(r['recid'], 1)

        # Score calculation testing.
        # For each file
        score1 = api.calculate_score([r['files_to_upload'][0]])
        score2 = api.calculate_score([r['files_to_upload'][1]])
        score3 = api.calculate_score([r['files_to_upload'][2]])
        self.assertEqual(score1, 40)
        self.assertEqual(score2, 100)
        self.assertEqual(score3, 100)
        # And the average
        avg = (sum([score1, score2, score3])) / 3  # 80
        self.assertEqual(api.calculate_score(r['files_to_upload']), avg)

    @patch('invenio.modules.records.api.get_record')
    def test_get_extension(self, get_record_mock):
        """Tests the get_extension method from the API.
        """
        r = RecordMock.get_mocked_record()
        self.assertEqual(
            api.get_file_extension(r['files_to_upload'][0][0]), '.xls')
        self.assertEqual(
            api.get_file_extension(r['files_to_upload'][1][0]), '.csv')
        self.assertEqual(
            api.get_file_extension(r['files_to_upload'][2][0]), '.pdf')
        self.assertEqual(api.get_file_extension('file/with/no/extension'), '')
        self.assertEqual(api.get_file_extension('file/with/no/name/.csv'), '')

    def test_get_name(self):
        files = ['first/file.csv', 'and-second/file2.doc']
        self.assertEqual(api.get_file_name(files[0]), 'first/file')
        self.assertEqual(api.get_file_name(files[1]), 'and-second/file2')

    def test_single_files(self):
        """Test a with some basic document types

        Types:
         - csv
         - pdf
         - xlsx
        """
        r = RecordMock.get_mocked_record()
        score = api.calculate_score(r['files_to_upload'])
        self.assertEqual(score, 80)

    """Tests concerning only the score calculation.

    No RecordMock needed, passing only file paths.
    """

    def test_docx_and_csv(self):
        """ CSV and DOCX should be 80
        """
        files = [
            ('word_document.docx', 'some/word_document.docx'),
            ('a.csv', 'and/a.csv'),
        ]
        self.assertEqual(api.calculate_score(files), 80)

    def test_csvs(self):
        """Everything csv should be 100
        """
        files = [
            ('something.csv', 'something.csv'),
            ('something-else.csv', 'something-else.csv'),
            ('thing.csv', 'and/also-this/thing.csv'),
        ]
        self.assertEqual(api.calculate_score(files), 100)

    def test_tar_with_pdf(self):
        files = [('something.ble', 'something.ble')]
        self.assertEqual(api.calculate_score(files), 0)

    def test_unknown_extension(self):
        """Test if unknow or invalid extensions produce 0 score
        """
        files = [('something.ble', 'something.ble'),
                 ('something', 'something')]
        self.assertEqual(api.calculate_score(files), 0)

    def test_fake_zip(self):
        """Tests a fake zip (bad) file.
        """
        files = [('fake.zip', 'this/is/a/fake.zip')]
        self.assertEqual(api.calculate_score(files), 0)

    def test_fake_tar(self):
        files = [('something.tar', 'something.tar')]
        api.calculate_score(files)

    def test_zip_with_txt_csv(self):
        """Tests a zip file with a txt and csv.

        Creates a temporary dir and adds the two files inside.
        Then creates the archive inside another temporary dir.
        Score should be 100.
        Deletes directories upon finishing.
        """

        # Create a dir to store the files
        tmp_dir = tempfile.mkdtemp()
        # Create a txt file inside tmp_dir
        with open(osp.join(tmp_dir, 'file.txt'), 'w') as txt_file:
            txt_file.write('batata')
        # Create a csv file inside tmp_dir
        with open(osp.join(tmp_dir, 'file.csv'), 'w') as csv_file:
            csv_file.write('123, 123')

        # Create another temporary dir for the zip file.
        tmp_zip_dir = tempfile.mkdtemp()
        # And make an archive out of it
        zip_file = make_archive(osp.join(tmp_zip_dir, '_zip_with_txt_csv'),
                                'zip',
                                tmp_dir)
        self.assertEqual(
            api.calculate_score([(osp.basename(zip_file), zip_file)]),
            100
        )

        # Remove the temporary directories
        rmtree(tmp_dir)
        rmtree(tmp_zip_dir)

        # Test if the files were removed
        self.assertEqual(osp.isdir(tmp_dir), False)
        self.assertEqual(osp.isdir(tmp_zip_dir), False)

        # Redundant.. directory is deleted.
        self.assertEqual(osp.exists(zip_file), False)
        self.assertEqual(osp.exists(txt_file.name), False)
        self.assertEqual(osp.exists(csv_file.name), False)

    def test_tar_with_txt_csv(self):
        """Tests a tar file with a txt and csv.

        Creates a temporary dir and adds the two files inside.
        Then creates the archive inside another temporary dir.
        Score should be 100.
        Deletes directories upon finishing.
        """

        # Create a dir to store the files
        tmp_dir = tempfile.mkdtemp()
        # Create a txt file inside tmp_dir
        with open(osp.join(tmp_dir, 'file.txt'), 'w') as txt_file:
            txt_file.write('batata')
        # Create a csv file inside tmp_dir
        with open(osp.join(tmp_dir, 'file.csv'), 'w') as csv_file:
            csv_file.write('123, 123')

        # Create another temporary dir for the zip file.
        tmp_tar_dir = tempfile.mkdtemp()
        # And make an archive out of it
        tar_file = make_archive(osp.join(tmp_tar_dir, '_tar_with_txt_csv'),
                                'tar',
                                tmp_dir)

        self.assertEqual(
            api.calculate_score([(osp.basename(tar_file), tar_file)]),
            100
        )

        # Remove the temporary directories
        rmtree(tmp_dir)
        rmtree(tmp_tar_dir)

        # Test if the files were removed
        self.assertEqual(osp.isdir(tmp_dir), False)
        self.assertEqual(osp.isdir(tmp_tar_dir), False)

        # Redundant.. directory is deleted.
        self.assertEqual(osp.exists(tar_file), False)
        self.assertEqual(osp.exists(txt_file.name), False)
        self.assertEqual(osp.exists(csv_file.name), False)


TEST_SUITE = make_test_suite(CalculateScoreTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
