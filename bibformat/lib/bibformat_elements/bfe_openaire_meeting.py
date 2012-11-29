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

import cgi
import time

#from invenio.openaire_deposit_config import CFG_OPENAIRE_THESIS_TYPES
from invenio.messages import gettext_set_language

def format_element(bfo):
    ln = bfo.lang
    _ = gettext_set_language(ln)

    info = bfo.field('711__')

    if not info:
        return ""

    ret = []
    if 'a' in info and 'g' in info:
        ret.append("%(a)s (%(g)s)")
    elif 'a' in info:
        ret.append("%(a)s")

    if 'c' in info:
        ret.append("%(c)s")
    if 'w' in info:
        ret.append("%(w)s")
    if 'd' in info:
        ret.append("%(d)s")

    ret = ", ".join(ret)
    ret = "%s." % ret

    return ret % info


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
