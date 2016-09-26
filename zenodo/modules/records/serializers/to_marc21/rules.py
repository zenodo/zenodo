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

"""MARC21 rules."""

from __future__ import absolute_import, print_function

from dojson import utils
from dojson.contrib.to_marc21 import to_marc21


@to_marc21.over('980', '^(resource_type|communities)$')
@utils.for_each_value
@utils.filter_values
def reverse_resource_type(dummy_self, key, value):
    """Reverse - Resource Type."""
    if key == 'resource_type':
        return {
            'a': value.get('type'),
            'b': value.get('subtype'),
            '$ind1': '_',
            '$ind2': '_',
        }
    elif key == 'communities':
        return {
            'a': 'user-{0}'.format(value),
            '$ind1': '_',
            '$ind2': '_',
        }


@to_marc21.over('999', '^references$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_references(dummy_self, dummy_key, value):
    """Reverse - References - raw reference."""
    return {
        'x': value.get('raw_reference'),
        '$ind1': 'C',
        '$ind2': '5',
    }


@to_marc21.over('942', '^embargo_date$')
@utils.filter_values
def reverse_embargo_date(dummy_self, dummy_key, value):
    """Reverse - embargo date."""
    return {
        'a': value,
        '$ind1': '_',
        '$ind2': '_',
    }


@to_marc21.over('909', '^(_oai|journal)$')
@utils.filter_values
def reverse_oai(dummy_self, key, value):
    """Reverse - OAI/Journal."""
    if key == '_oai':
        return {
            'o': value.get('id'),
            'p': utils.reverse_force_list(value.get('sets')),
            '$ind1': 'C',
            '$ind2': 'O',
        }
    elif key == 'journal':
        return {
            'n': value.get('issue'),
            'c': value.get('pages'),
            'v': value.get('volume'),
            'p': value.get('title'),
            'y': value.get('year'),
            '$ind1': 'C',
            '$ind2': '4',
        }
    return


@to_marc21.over('856', '^conference_url$')
@utils.filter_values
def reverse_conkerence_url(dummy_self, key, value):
    """Reverse - Meeting."""
    return {
        'y': 'Conference website',
        'u': value,
        '$ind1': '4',
        '$ind2': '_',
    }
