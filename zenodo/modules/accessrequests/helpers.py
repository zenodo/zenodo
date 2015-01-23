# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
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

from sqlalchemy.sql.expression import desc


class Ordering(object):

    """Helper class for column sorting."""

    def __init__(self, options, selected):
        self.options = options
        if selected in options:
            self._selected = selected
            self.asc = True
        elif selected and selected[0] == '-' and selected[1:] in options:
            self._selected = selected[1:]
            self.asc = False
        else:
            self._selected = None
            self.asc = None

    def reverse(self, col):
        if col in self.options:
            if self.is_selected(col):
                return col if not self.asc else '-{0}'.format(col)
            else:
                return col
        return None

    def dir(self, col, asc='asc', desc='desc'):
        if col == self._selected and self.asc is not None:
            return asc if self.asc else desc
        else:
            return None

    def is_selected(self, col):
        return col == self._selected

    def selected(self):
        return self._selected if self.asc else "-{0}".format(self._selected)


class QueryOrdering(Ordering):
    def __init__(self, query, options, selected):
        super(QueryOrdering, self).__init__(options, selected)
        self.query = query

    def items(self):
        if self.asc is not None:
            if self._selected and self.asc:
                return self.query.order_by(self._selected)
            elif self._selected and not self.asc:
                return self.query.order_by(desc(self._selected))
        return self.query
