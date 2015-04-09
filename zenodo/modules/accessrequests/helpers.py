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

"""Helper classes to make working with column ordering in templates easier."""

from sqlalchemy.sql.expression import desc


class Ordering(object):

    """Helper class for column sorting."""

    def __init__(self, options, selected):
        """Initialize ordering with possible options the selected option.

        :param options: List of column options.
        :param selected: Selected column. Prefix name with ``-`` to denote
            descending ordering.
        """
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
        """Get reverse direction of ordering."""
        if col in self.options:
            if self.is_selected(col):
                return col if not self.asc else '-{0}'.format(col)
            else:
                return col
        return None

    def dir(self, col, asc='asc', desc='desc'):
        """Get direction (ascending/descending) of ordering."""
        if col == self._selected and self.asc is not None:
            return asc if self.asc else desc
        else:
            return None

    def is_selected(self, col):
        """Determine if column is being order by."""
        return col == self._selected

    def selected(self):
        """Get column which is being order by."""
        if self._selected:
            return self._selected if self.asc else \
                "-{0}".format(self._selected)
        return None


class QueryOrdering(Ordering):

    """Helper class for column sorting based on SQLAlchemy queries."""

    def __init__(self, query, options, selected):
        """Initialize with SQLAlchemy query."""
        super(QueryOrdering, self).__init__(options, selected)
        self.query = query

    def items(self):
        """Get query with correct ordering."""
        if self.asc is not None:
            if self._selected and self.asc:
                return self.query.order_by(self._selected)
            elif self._selected and not self.asc:
                return self.query.order_by(desc(self._selected))
        return self.query
