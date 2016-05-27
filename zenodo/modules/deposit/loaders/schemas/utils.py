# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Marshmallow schemas cleaning utility functions."""

from __future__ import absolute_import, print_function


def is_true_value(value):
    """Conditional for regarding a value as 'true', i.e. non-empty.

    True for all integers (including zero) and non-empty string, dict, list.
    """
    if isinstance(value, int):
        return True
    else:
        return bool(value)


def is_valid(keys=None):
    """Conditional function for 'valid' dictionary values.

    Can be used to filer-out 'non-valid' values such as 'None'
    values, empty lists, or dictionaries with empty items.

    :param keys: Only if value is a dict.
                 Treat the item as 'valid' if value of any of the
                 'keys' resolves as True.  If keys is None,
                 keep if *any* value in the dictionary resolves as True.
    :type keys: list
    """
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and is_true_value(v):
                    return True
            return False
        elif isinstance(elem, list):
            return len(elem) > 0
        elif isinstance(elem, str):
            return elem != ''
        else:
            return elem is not None
    return _inner


def _remove_empty_keys(nested=True):
    """Strip the dictionary from keys with non-true values.

    :param nested: if True, call recursively for all values
    :type nested: bool
    :returns: empty keys stripping function
    :rtype: function
    """
    def _inner(elem):
        strip_value = _remove_empty_keys(nested=nested) if nested \
            else (lambda x: x)
        if isinstance(elem, dict):
            return dict((k, strip_value(v))
                        for k, v in elem.items() if is_true_value(v))
        if isinstance(elem, list):
            return list(strip_value(i) for i in elem
                        if is_true_value(i))
        else:
            return elem
    return _inner


def filter_empty_list(keys=None, remove_empty_keys=False):
    """Apply the non-empty check to a list of elements.

    :param remove_empty_keys: Flag if all empty keys should be removed.
    :type remove_empty_keys: bool
    """
    def _inner(elems):
        new_elems = list(filter(is_valid(keys=keys),
                                elems))
        if remove_empty_keys:
            new_elems = list(map(_remove_empty_keys(nested=True), new_elems))
        return new_elems
    return _inner


def filter_thesis(keys=None):
    """Apply the non-filter check to thesis.

    The keys parameter is passed to the 'supervisors' list filter.

    :param keys: Keys (any of) required to keep an item during filtering.
    :type keys: list
    """
    def _inner(thesis):
        if 'supervisors' in thesis:
            func = filter_empty_list(keys=keys)
            thesis['supervisors'] = func(thesis['supervisors'])
            if not thesis['supervisors']:
                del thesis['supervisors']
        if 'university' in thesis and not thesis['university']:
            del thesis['university']
        return thesis
    return _inner


def none_if_empty(keys=None):
    """Apply the non-empty-check to a dictionary value."""
    def _inner(elem):
        return elem if is_valid(keys=keys)(elem) else None
    return _inner
