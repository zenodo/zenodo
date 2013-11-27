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

from invenio.flaskshell import *
from invenio.errorlib import register_exception
from invenio.search_engine import search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field
from invenio.bibupload import bibupload

try:
    from altmetric import Altmetric, AltmetricHTTPException
except ImportError, e:
    register_exception(prefix='Altmetric module not installed: %s' % str(e),
                                           alert_admin=False)


def bst_openaire_altmetric():
    """
    """
    recids = search_pattern(p="0->Z", f="0247_a")
    a = Altmetric()

    for recid in recids:
        try:
            # Check if we already have an Altmetric id
            sysno_inst = get_fieldvalues(recid, "035__9")
            if ['Altmetric'] in sysno_inst:
                continue

            doi_val = get_fieldvalues(recid, "0247_a")[0]
            json_res = a.doi(doi_val)

            rec = {}
            record_add_field(rec, "001", controlfield_value=str(recid))

            if json_res:
                record_add_field(rec, '035', subfields=[('a',
                    str(json_res['altmetric_id'])), ('9', 'Altmetric')])
                bibupload(rec, opt_mode='correct')
        except AltmetricHTTPException, e:
            register_exception(prefix='Altmetric error (status code %s): %s' %
                (e.status_code, str(e)), alert_admin=False)


if __name__ == '__main__':
    bst_openaire_altmetric()
