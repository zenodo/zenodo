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
import os
from invenio.base.globals import cfg
# from invenio.modules.records.api import get_record

# get_record(recid)

# from invenio.legacy.bibdocfile.api import BibRecDocs
#         return dict(
#             zenodo_files=[f for f in BibRecDocs(
#                 kwargs['recid'], human_readable=True
#             ).list_latest_files(
#                 list_hidden=False
#             ) if not f.is_icon()]
#         )

def calculate_score(recid):
    '''
    TODO:
        * Pass files by argument
        * Use fido for file verification
    '''
    cfg['PRESERVATIONMETER_dfdfd']
    ## Map of quality per file type per category
    ext_quality = {'.csv': 100,
                   '.pdf': 100,
                   '.txt': 95,
                   '.odt': 95,
                   '.xlsx': 60,
                   '.docx': 60,
                   '.xls': 40,
                   '.doc': 40}

    ## List of files to parse
    ## Use the API to get the list.
    file_list = ['text.txt', 'data.csv']

    ## Storing qualities
    ## Iterate the list and get the file extension and quality associated.
    files_quality = []
    for file in file_list:
        file_name, file_ext = os.path.splitext(file)
        files_quality.append(ext_quality[file_ext])
        # print '[{}{}] preservation status: {}'.format(file_name,
        #                                               file_ext,
        #                                               ext_quality[file_ext])

    ## Average quality of this submission
    #print files_quality
    sum = 0
    for quality in files_quality:
        sum += quality

    #print sum / len(files_quality)
    sum / len(files_quality)
