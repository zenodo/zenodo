# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

"""FP7 prject facet"""

from invenio.websearch_facet_builders import FacetBuilder


class AccessRightsFacetBuilder(FacetBuilder):

    def _prepare_value(self, val):
        return (val[0].split("-")[0].strip(), val[1])

    def get_title(self, **kwargs):
        return "Any Access right"

    def get_facets_for_query(self, *args, **kwargs):
        return super(AccessRightsFacetBuilder, self).get_facets_for_query(
            *args, **kwargs)

facet = AccessRightsFacetBuilder('access_rights', order=2)
