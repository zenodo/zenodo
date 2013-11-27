#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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
Tasklets to update the list of OpenAIRE keywords to match any edits
made in the records. 
"""

from invenio.bibdocfile import BibRecDocs
from invenio.bibtask import write_message, task_update_progress, \
    task_sleep_now_if_required
from invenio.openaire_deposit_config import CFG_ACCESS_RIGHTS_KEYS
from invenio.search_engine import search_pattern, get_fieldvalues

def bst_openaire_check_rights():
    """
    Tasklet to verify access rights consistency.
    """
    restrictions = {
        'cc0' : '',
        'openAccess' : '',
        'closedAccess' : 'status: closedAccess',
        'restrictedAccess' : 'status: restrictedAccess',
        'embargoedAccess' : 'firerole: deny until "%(date)s"\nallow any',
    }

    errors = []

    for access_rights in CFG_ACCESS_RIGHTS_KEYS:
        write_message("Checking records with access rights '%s'" % access_rights)
        recids = search_pattern(p=access_rights, f="542__l")

        for r in recids:
            date = ''
            if access_rights == 'embargoedAccess':
                try:
                    date = get_fieldvalues(r, "942__a")[0]
                except IndexError:
                    raise Exception("Embargoed record %s is missing embargo date in 942__a" % r)
            expected_status = restrictions[access_rights] % { 'date' : date }

            brd = BibRecDocs(r)
            for d in brd.list_bibdocs():
                real_status = d.get_status()
                if real_status != expected_status:
                    d.set_status(expected_status)
                    write_message("Fixed record %s with wrong status. From: %s To: %s" % (r, real_status, expected_status))

    for e in errors:
        write_message(e)

if __name__ == '__main__':
    bst_openaire_check_rights()
