#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Generate MARC XML file for correcting MARC field 8564_u (file links)

Run as::
  python fix_8560.py > output.xml
  bibupload -c output.xml
"""
from invenio.flaskshell import *
from invenio.search_engine import search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field, record_xml_output
from invenio import config


def replace_link_func(from_base, to_base):
    def replace_link(x):
            if x.startswith(from_base):
                return x.replace(from_base, to_base)
            else:
                return x

    return replace_link


def main():
    from_base = 'http://openaire.cern.ch'
    to_base = config.CFG_SITE_URL

    # All records
    recids = search_pattern(p="0->Z", f="8564_u")

    print "<collection>"
    for recid in recids:
        # Get record information
        touched = False
        file_links = get_fieldvalues(recid, "8564_u")

        new_file_links = map(replace_link_func(from_base, to_base), file_links)

        # Print correcting to record
        rec = {}
        record_add_field(rec, "001", controlfield_value=str(recid))
        for old_link, new_link in zip(file_links, new_file_links):
            if old_link != new_link:
                touched = True
            record_add_field(rec, '856', ind1='4', subfields=[('u', new_link)])

        if touched:
            print record_xml_output(rec)
    print "</collection>"


if __name__ == "__main__":
    main()
