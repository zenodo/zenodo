# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2008, 2009, 2010, 2011 CERN.
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
"""BibFormat element - Prints publisher name
"""
__revision__ = "$Id$"

from invenio.search_engine import get_all_collections_of_a_record, \
    create_navtrail_links

def format_element(bfo, separator="<br />"):
    """Prints the list of collections the record belongs to.

    @param separator: a separator between each collection link.
    """
    def _include(collname):
        return not (collname.startswith('provisional-') or
                    collname == 'zenodo-public' or collname == 'user-zenodo')

    coll_names = filter(_include, get_all_collections_of_a_record(bfo.recID))

    navtrails = [create_navtrail_links(coll_name, ln=bfo.lang) for coll_name in coll_names]
    navtrails = [navtrail for navtrail in navtrails if navtrail]
    navtrails.sort(lambda x, y: cmp(len(y), len(x)))
    final_navtrails = []
    for navtrail in navtrails:
        for final_navtrail in final_navtrails:
            if navtrail in final_navtrail:
                break
        else:
            final_navtrails.append(navtrail)
    return separator.join(final_navtrails)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
