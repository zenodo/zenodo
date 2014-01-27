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

from flask import current_app
from invenio.base.i18n import _

def format_element(bfo, as_label=False):
    ln = bfo.lang
    collections = bfo.fields('980__')

    # Loop over collection identifiers. First 980 entry that has a publication
    # type in subfield a is used. Subfield b denotes a subtype.
    #
    # Other non-publication type 980 entries include user collection
    # identifiers, and ZENODO specific identifiers like "curated".

    CFG_OPENAIRE_PUBTYPE_MAP = current_app.config['CFG_OPENAIRE_PUBTYPE_MAP']
    for c in collections:
        try:

            collection = c.get('a')
            subcollection = c.get('b', None)

            name = _(dict(CFG_OPENAIRE_PUBTYPE_MAP)[collection])
            query = "980__a:%s" % collection

            if subcollection:
                name = _(dict(CFG_OPENAIRE_PUBTYPE_MAP)[subcollection])
                query = "980__b:%s" % subcollection

            if as_label:
                return """<a href="/search?p=%s" class="label label-inverse">%s</a>""" % (query, name)
            else:
                return name
        except KeyError:
            pass


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
