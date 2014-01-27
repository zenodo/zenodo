# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
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

"""FP7 prject facet"""

from invenio.modules.search.facet_builders import FacetBuilder


class AccessRightsFacetBuilder(FacetBuilder):

    def _prepare_value(self, val):
        return (val[0].split("-")[0].strip(), val[1])

    def get_title(self, **kwargs):
        return "Any Access right"

    def get_facets_for_query(self, *args, **kwargs):
        return super(AccessRightsFacetBuilder, self).get_facets_for_query(
            *args, **kwargs)

facet = AccessRightsFacetBuilder('access_rights', order=2)
