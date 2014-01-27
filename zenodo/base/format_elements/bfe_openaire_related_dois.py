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

from invenio.base.i18n import gettext_set_language


def format_element(bfo, title='Related DOIs', type=None):
    ln = bfo.lang

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

    return "%(related_doi_str)s" % {
        'related_doi_str': related_doi_str,
    }


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
