# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
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

from invenio.openaire_deposit_config import CFG_OPENAIRE_PUBTYPE_MAP


def format_element(bfo, as_label=False):
    ln = bfo.lang
    collection = bfo.field('980__a')
    if not collection:
        collection = bfo.field('980__b')

    if as_label:
        return """<span class="label label-inverse">%s</span>""" % dict(CFG_OPENAIRE_PUBTYPE_MAP(ln))[collection]
    else:
        return dict(CFG_OPENAIRE_PUBTYPE_MAP(ln))[collection]


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
