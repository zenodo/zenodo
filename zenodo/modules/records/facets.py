# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

"""Facets factory for REST API."""

from __future__ import absolute_import, print_function

import re
from decimal import Decimal, InvalidOperation

from elasticsearch_dsl import Q
from invenio_rest.errors import FieldError, RESTValidationError

from zenodo.modules.records import current_custom_metadata


def geo_bounding_box_filter(name, field, type=None):
    """Create a geo bounding box filter.

    :param field: Field name.
    :param type: Method to use (``memory`` or ``indexed``).
    :returns: Function that returns the Geo bounding box query.
    """
    def inner(values):
        if len(values) != 1:
            raise RESTValidationError(
                errors=[FieldError(name, 'Only one parameter is allowed.')])
        values = [value.strip() for value in values[0].split(',')]
        if len(values) != 4:
            raise RESTValidationError(
                errors=[FieldError(
                    name,
                    'Invalid bounds: four comma-separated numbers required. '
                    'Example: 143.37158,-38.99357,146.90918,-37.35269')])

        try:
            bottom_left_lon = Decimal(values[0])
            bottom_left_lat = Decimal(values[1])
            top_right_lon = Decimal(values[2])
            top_right_lat = Decimal(values[3])
        except InvalidOperation:
            raise RESTValidationError(
                errors=[FieldError(name, 'Invalid number in bounds.')])
        try:
            if not (-90 <= bottom_left_lat <= 90) or \
                    not (-90 <= top_right_lat <= 90):
                raise RESTValidationError(
                    errors=[FieldError(
                        name, 'Latitude must be between -90 and 90.')])
            if not (-180 <= bottom_left_lon <= 180) or \
                    not (-180 <= top_right_lon <= 180):
                raise RESTValidationError(
                    errors=[FieldError(
                        name, 'Longitude must be between -180 and 180.')])
        except InvalidOperation:  # comparison with "NaN" raises exception
            raise RESTValidationError(
                errors=[FieldError(
                    name, 'Invalid number: "NaN" is not a permitted value.')])

        query = {
            field: {
                'top_right': {
                    'lat': top_right_lat,
                    'lon': top_right_lon,
                },
                'bottom_left': {
                    'lat': bottom_left_lat,
                    'lon': bottom_left_lon,
                }
            }
        }

        if type:
            query['type'] = type
        return Q('geo_bounding_box', **query)

    return inner


def custom_metadata_filter(field):
    """Custom metadata fields filter.

    :param field: Field name.
    :returns: Function that returns the custom metadata query.
    """
    def inner(values):
        definitions = current_custom_metadata.definitions
        terms = current_custom_metadata.terms
        must_conditions = []
        for value in values:
            # Matches one of:
            #
            #   community[vocabulary:term]:value
            #   [vocabulary:term]:value
            parsed = re.match(r'([-\w]+)?\[([-\w]+\:[-\w]+)\]\:(.+)', value)
            if not parsed:
                raise RESTValidationError(
                    errors=[FieldError(
                        field, 'The parameter should have the format: '
                               'custom=community[field_name]:filed_value.')])

            community, search_key, search_value = parsed.groups()

            # check if the community supports custom fields
            if community and community not in definitions:
                raise RESTValidationError(
                    errors=[FieldError(field, 'The "{}" community does not '
                            'support custom metadata.'.format(community))])

            # check if the field is supported by the community
            if community and search_key not in definitions[community]:
                raise RESTValidationError(
                    errors=[FieldError(
                        field, 'The "{}" term is not supported by the "{}" '
                        'community.'.format(search_key, community))])
            elif search_key not in terms:
                raise RESTValidationError(
                    errors=[FieldError(
                        field, 'The "{}" term is not supported.'
                        .format(search_key))])

            # TODO: check if the search value has the correct type
            # for now we have only 'keyword' and 'text'

            # TODO: move this to a central place
            # get the elasticsearch custom field name
            custom_fields_mapping = dict(
                keyword='custom_keywords',
                text='custom_text'
            )

            custom_type = terms[search_key]
            es_field = custom_fields_mapping[custom_type]

            must_conditions.append({
                'nested': {
                    'path': es_field,
                    # 'score_mode': 'avg',
                    'query': {
                        'bool': {'must': [
                            {'match': {es_field + '.key': search_key}},
                            {'match': {es_field + '.value': search_value}}
                            # TODO: in the future also filter ".community"
                        ]}
                    }
                }
            })
        return Q('bool', must=must_conditions)
    return inner
