# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo schema.org marshmallow schema."""

from __future__ import absolute_import, print_function, unicode_literals

from marshmallow import Schema, fields, missing


class Feature(Schema):
    """Schema for Feature."""

    type_ = fields.Constant('Feature', dump_to='type')
    geometry = fields.Method('get_locations')
    properties = fields.Method('get_name')

    def get_locations(self, obj):
        """Get locations of the record."""
        if obj.get('lat') and obj.get('lon'):
            return {
                "type": "Point",
                "coordinates": [obj['lon'], obj['lat']]
            }
        else:
            return missing

    def get_name(self, obj):
        """Get name of the record."""
        return {"name": obj['place']}


class FeatureCollection(Schema):
    """Schema for FeatureCollection."""

    features = fields.Method('get_locations')

    type_ = fields.Constant('FeatureCollection', dump_to='type')

    def get_locations(self, obj):
        """Get locations."""
        s = Feature()
        items = []
        for l in obj['metadata'].get('locations', []):
            if l.get('lat') and l.get('lon'):
                items.append(s.dump({
                    'lat': l['lat'], 'lon': l['lon'], 'place': l['place']
                }).data)

        return items
