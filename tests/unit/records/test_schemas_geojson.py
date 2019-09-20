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

"""Zenodo GeoJSON mapping test."""

from zenodo.modules.records.serializers import geojson_v1


def test_full_record(db, record_with_bucket, recid_pid):
    """Test full record metadata."""
    _, full_record_model = record_with_bucket
    obj = geojson_v1.transform_record(recid_pid, full_record_model)

    expected = {
        u'features': [{
            u'geometry': {
                u'coordinates': [1.534, 2.35],
                u'type': u'Point'
            },
            u'properties': {
                u'name': u'my place'
            },
            u'type': u'Feature'}
        ],
        u'type': u'FeatureCollection'
    }

    assert obj == expected
