# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2007, 2008, 2009, 2010, 2011 CERN.
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


from invenio.config import CFG_SITE_RECORD


def format_element(bfo, with_ln="yes"):
    """
    Prints the record URL.

    @param with_ln: if "yes" include "ln" attribute in the URL
    """
    url = ("/%s/" % CFG_SITE_RECORD) + bfo.control_field('001')

    if with_ln.lower() == "yes":
        url += "?ln=" + bfo.lang

    return url
