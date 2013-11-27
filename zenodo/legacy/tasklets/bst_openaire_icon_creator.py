# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
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

"""
"""

import os
from invenio.flaskshell import *
from invenio.dbquery import run_sql
from invenio.bibdocfile import BibDoc, InvenioBibDocFileError
from invenio.websubmit_icon_creator import create_icon, \
    InvenioWebSubmitIconCreatorError
from invenio.errorlib import register_exception


def bst_openaire_icon_creator():
    """
    """
    docs = run_sql("""
        SELECT f.id_bibdoc
        FROM bibdocfsinfo AS f
        LEFT OUTER JOIN (
            SELECT DISTINCT id_bibdoc, 1
            FROM bibdocfsinfo
            WHERE format LIKE '%;icon' AND last_version=1
        ) AS i ON i.id_bibdoc=f.id_bibdoc
        WHERE i.id_bibdoc is null""")

    icon_size = "90"
    format = "png"

    for docid, in docs:
        d = BibDoc(docid)
        if not d.get_icon():
            for f in d.list_latest_files():
                if not f.is_icon():
                    file_path = f.get_full_path()
                    try:
                        filename = os.path.splitext(os.path.basename(file_path))[0]
                        (icon_dir, icon_name) = create_icon(
                            {'input-file': file_path,
                             'icon-name': "icon-%s" % filename,
                             'multipage-icon': False,
                             'multipage-icon-delay': 0,
                             'icon-scale': icon_size,
                             'icon-file-format': format,
                             'verbosity': 0})
                        icon_path = os.path.join(icon_dir, icon_name)
                    except InvenioWebSubmitIconCreatorError, e:
                        register_exception(prefix='Icon for file %s could not be created: %s' % \
                                           (file_path, str(e)),
                                           alert_admin=False)

                    try:
                        if os.path.exists(icon_path):
                            d.add_icon(icon_path)
                    except InvenioBibDocFileError, e:
                        register_exception(prefix='Icon %s for file %s could not be added to document: %s' % \
                                           (icon_path, f, str(e)),
                                           alert_admin=False)


if __name__ == '__main__':
    bst_openaire_icon_creator()
