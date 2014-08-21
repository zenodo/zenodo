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

from __future__ import print_function
from os.path import splitext
from invenio.base.globals import cfg
import zipfile, tarfile


def get_file_extension(file_path):
    '''
    Returns only the extension of a given file.
    '''
    file_name, file_ext = splitext(file_path)
    return file_ext


def get_file_name(file_path):
    '''
    Returns only the file name of a given file.
    '''
    file_name, file_ext = splitext(file_path)
    return file_name


def calculate_score(file_path_list):
    """Receives a list of file paths and calculates their preservation score.
    """
    ## Iterate the list and get the file extension and quality associated.
    files_quality = []
    for file_p in file_path_list:
        if is_file_compressed(file_p):
            ## Try to extract it
            for extracted_file in extractor(file_p):
                ## Extract one level of files and append them
                files_quality.append(calculate_file_score(extracted_file))
        else:
            files_quality.append(calculate_file_score(file_p))

    ## Average quality of this submission
    return sum(files_quality) / len(files_quality)

def extractor(file_name):
    """Generator to iterate through files inside an archive.
    """
    ## ZipFiles
    try:
        if zipfile.is_zipfile(file_name):
            z = zipfile.ZipFile(file_name, "r")
            for file_p in z.namelist():
                yield file_p
        elif tarfile.is_tarfile(file_name):
            print("### oh noes a tar file")
            print(file_name)
            yield 'bad/file.bad'
        else:
            raise
    except:
        yield 'bad/file.bad'

def calculate_file_score(file_name):
    """Returns the associated score of this extension.

    As defined on cfg.
    """
    file_ext = get_file_extension(file_name)
    return cfg['PRESERVATIONMETER_FILES_QUALITY'].get(file_ext) or 0

def is_file_compressed(file_name):
    """Returns if a file is in a known compressed format.
    """
    list_of_compressed_formats = ['.zip', 'tar']
    return get_file_extension(file_name) in list_of_compressed_formats
