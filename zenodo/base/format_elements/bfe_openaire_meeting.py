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

import cgi
import time
from invenio.base.i18n import gettext_set_language

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
