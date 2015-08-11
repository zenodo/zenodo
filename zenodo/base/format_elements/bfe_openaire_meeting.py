# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


def format_element(bfo):

    info = bfo.field('711__')
    conf_link = bfo.field('8564_u')

    if not info:
        return ""

    ret = []
    if 'a' in info:
        if 'g' in info:
            name_format = "%(a)s (%(g)s)"
        else:
            name_format = "%(a)s"
        if conf_link:
            name_format = "<a href='%s'>%s</a>" % (conf_link, name_format)
        ret.append(name_format)

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
