# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Unit tests Zenodo JSON schemas utils."""

from __future__ import absolute_import, print_function

from zenodo.modules.jsonschemas.utils import merge_dicts


def test_merge_dicts(app):
    """Test jsonschema merging util."""
    a1 = {
        'd': {
            'k1': 1,
            'k2': 'v2',
            'd2': {
                'k3': 'v3',
            },
        },
        'l': [1, 2, 3, ],
    }
    b1 = {
        'd': {
            'k1': 10,  # Updated value in nested
            'k2': 'v2',
            'k3': 'v3',  # New key in nested
            'd2': {
                'k4': 'v4',
            },

        },
        'l': [4, 5, 6, ],  # Updated list
        'v': 'value',  # New key at root
    }
    exp1 = {
        'd': {
            'k1': 10,
            'k2': 'v2',
            'k3': 'v3',
            'd2': {
                'k3': 'v3',
                'k4': 'v4',
            },
        },
        'l': [4, 5, 6, ],
        'v': 'value',
    }
    ab1 = merge_dicts(a1, b1)
    assert ab1 == exp1
