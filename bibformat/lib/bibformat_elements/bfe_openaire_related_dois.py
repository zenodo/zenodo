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

from invenio.messages import gettext_set_language


def format_element(bfo, title='Related DOIs', type=None):
    ln = bfo.lang
    _ = gettext_set_language(ln)

    related_dois = bfo.fields('773__')
    related_doi_str = []

    for field in related_dois:
        # Remove DOIs not of this type
        if type:
            try:
                if field['n'] != type:
                    continue
            except KeyError:
                continue
        related_doi_str.append(field['a'])

    if not related_doi_str:
        return ""

    related_doi_str = ", ".join(["<a href=\"http://dx.doi.org/%(doi)s\">%(doi)s</a>" % {'doi': x} for x in related_doi_str])

    return "%(x_fmt_s)s%(title)s%(x_fmt_e)s: %(related_doi_str)s" % {
        'x_fmt_s': "<strong>",
        'x_fmt_e': "</strong>",
        'title': _(title),
        'related_doi_str': related_doi_str,
    }


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
