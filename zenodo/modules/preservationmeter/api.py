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


def get_file_extension(file_path):
    '''
    Returns only the extension of a given file
    '''
    from os.path import splitext
    file_name, file_ext = splitext(file_path)
    return file_ext


def get_file_name(file_path):
    '''
    Returns only the file name of a given file
    '''
    from os.path import splitext
    file_name, file_ext = splitext(file_path)
    return file_name


def calculate_score(file_path_list):
    """
    TODO:
        * Pass files by argument
        * Use fido for file verification
    """
    ## Iterate the list and get the file extension and quality associated.
    files_quality = []
    for file_p in file_path_list:
        files_quality.append(calculate_file_score(file_p))

    ## Average quality of this submission
    return sum(files_quality) / len(files_quality)


def calculate_file_score(file_name):
    """Returns the associated score of this extension.

    As defined on cfg.
    """
    file_ext = get_file_extension(file_name)
    ext_quality = {'.csv': 100,
                   '.pdf': 100,
                   '.txt': 95,
                   '.odt': 95,
                   '.xlsx': 60,
                   '.docx': 60,
                   '.xls': 40,
                   '.doc': 40}
    return ext_quality.get(file_ext) or 0
