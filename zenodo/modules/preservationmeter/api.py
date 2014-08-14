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

#import fido
from __future__ import print_function
from invenio.base.globals import cfg
from flask import current_app
from invenio.modules.records.api import get_record

# get_record(recid)

# from invenio.legacy.bibdocfile.api import BibRecDocs
#         return dict(
#             zenodo_files=[f for f in BibRecDocs(
#                 kwargs['recid'], human_readable=True
#             ).list_latest_files(
#                 list_hidden=False
#             ) if not f.is_icon()]
#         )


def get_extension(file_path):
    '''
    Returns only the extension of a given file
    '''
    from os.path import splitext
    file_name, file_ext = splitext(file_path)
    return file_ext


def get_name(file_path):
    '''
    Returns only the file name of a given file
    '''
    from os.path import splitext
    file_name, file_ext = splitext(file_path)
    return file_name


#def calculate_score(file_path_list):
def calculate_score(recid):
    '''
    TODO:
        * Pass files by argument
        * Use fido for file verification
    '''
    #cfg['PRESERVATIONMETER_dfdfd']
    ## Map of quality per file type per category
    ext_quality = {'.csv': 100,
                   '.pdf': 100,
                   '.txt': 95,
                   '.odt': 95,
                   '.xlsx': 60,
                   '.docx': 60,
                   '.xls': 40,
                   '.doc': 40}

    ## Get the files from this record
    record = get_record(recid)
    #for ifile in record['files_to_upload']:
    #    print ifile['url']

    ##TODO: Use this? v
    #from invenio.legacy.bibdocfile.api import BibRecDocs
    # files = dict(
    #     zenodo_files=[f for f in BibRecDocs(
    #         recid, human_readable=True
    #     ).list_latest_files(
    #         list_hidden=False
    #     ) if not f.is_icon()]
    # )

    ## List of files to parse
    ## Use the API to get the list.
    #file_list = ['text.txt', 'data.csv']
    #file_list = record['_files'] -> Doesnt work
    file_list = record['files_to_upload']

    ## Storing qualities
    ## Iterate the list and get the file extension and quality associated.
    files_quality = []
    for ifile in file_list:
        file_ext = get_extension(ifile['url'])
        file_name = get_name(ifile['url'])
        files_quality.append(ext_quality[file_ext])
        current_app.logger.info('[{}{}] preservation status: {}'.format(
                                file_name,
                                file_ext,
                                ext_quality[file_ext]))

    ## Average quality of this submission
    return sum(files_quality) / len(files_quality)
