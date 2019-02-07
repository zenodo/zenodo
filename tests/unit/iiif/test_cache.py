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

"""Unit tests for thumbnail caching."""


def test_thumbnail_caching(app, iiif_cache):
    """Test thumbnail cache."""
    key_250 = 'iiif:identifier1/full/250,/default/0.png'
    key = 'iiif:identifier2/full/260,/default/0.jpg'
    value = 'value'

    # only images with size == (250,) are cached
    assert iiif_cache.get(key_250) is None
    iiif_cache.set(key_250, value)
    assert iiif_cache.get(key_250) == 'value'

    assert iiif_cache.get(key) is None
    iiif_cache.set(key, value)
    assert iiif_cache.get(key) is None
