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

"""Model tests."""

from __future__ import absolute_import

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

from ..helpers import Ordering, QueryOrdering


class OrderingTestCase(InvenioTestCase):

    """Test ordering helper class."""

    def test_selected(self):
        """Test selected."""
        self.assertEqual('a', Ordering(['a', 'b'], 'a').selected())
        self.assertEqual('-b', Ordering(['a', 'b'], '-b').selected())
        self.assertIsNone(Ordering(['a', 'b'], 'c').selected())
        self.assertIsNone(Ordering(['a', 'b'], None).selected())

    def test_reverse(self):
        """Test reverse."""
        self.assertEqual('-a', Ordering(['a', 'b'], 'a').reverse('a'))
        self.assertEqual('a', Ordering(['a', 'b'], '-a').reverse('a'))
        self.assertEqual('b', Ordering(['a', 'b'], 'a').reverse('b'))
        self.assertEqual('b', Ordering(['a', 'b'], '-a').reverse('b'))
        self.assertIsNone(Ordering(['a', 'b'], '-a').reverse('c'))

    def test_dir(self):
        """Test direction."""
        self.assertEqual('asc', Ordering(['a', 'b'], 'a').dir('a'))
        self.assertEqual('desc', Ordering(['a', 'b'], '-a').dir('a'))
        self.assertIsNone(Ordering(['a', 'b'], 'a').dir('b'))
        self.assertIsNone(Ordering(['a', 'b'], '-a').dir('b'))

    def test_is_selected(self):
        """Test selected."""
        self.assertTrue(Ordering(['a', 'b'], 'a').is_selected('a'))
        self.assertTrue(Ordering(['a', 'b'], '-a').is_selected('a'))
        self.assertFalse(Ordering(['a', 'b'], 'a').is_selected('b'))
        self.assertFalse(Ordering(['a', 'b'], '-a').is_selected('b'))


class QueryOrderingTestCase(InvenioTestCase):

    """Test query ordering test case."""

    class MockQuery():
        def order_by(self, val):
            return val

    def test_items(self):
        """Test selected."""
        q = self.MockQuery()
        self.assertEqual('a', QueryOrdering(q, ['a', 'b'], 'a').items())
        self.assertEqual(
            'a', QueryOrdering(q, ['a', 'b'], '-a').items().element.text
        )
        self.assertEqual(q, QueryOrdering(q, ['a', 'b'], 'c').items())


TEST_SUITE = make_test_suite(OrderingTestCase, QueryOrderingTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
