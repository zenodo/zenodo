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
Generate MARC XML file for correcting MARC field 8560_ (submitter)

Run as::
  python fix_8560.py > output.xml
  bibupload -c output.xml
"""

from invenio.search_engine import search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.webuser import collect_user_info, get_uid_from_email

# All records
recids = search_pattern(p="0->Z", f="8560_f")

print "<collection>"
for recid in recids:
    # Get record information
    email = get_fieldvalues(recid, "8560_f")[0]
    if "<" in email:
        email = email.split()[-1][1:-1].strip()
    user_info = collect_user_info(get_uid_from_email(email))
    name = user_info.get("external_fullname", user_info.get("nickname", ""))
    external_id = user_info.get("external_id", "")

    # Create correction for record
    rec = {}
    record_add_field(rec, "001", controlfield_value=str(recid))
    record_add_field(rec, '856', ind1='0', subfields=[('f', email), ('y', name)])
    print record_xml_output(rec)
print "</collection>"