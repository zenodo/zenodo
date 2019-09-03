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

"""Test for OpenAIRE extension."""

from __future__ import absolute_import, print_function

from zenodo.modules.openaire import current_openaire


def test_openaire_type(app):
    """Test OpenAIRE type."""
    assert set(current_openaire.inverse_openaire_community_map.keys()) == \
        set(['c1', 'c2', 'c3'])

    assert set(current_openaire.inverse_openaire_community_map['c1']) == \
        set(['foo', 'bar'])
    assert set(current_openaire.inverse_openaire_community_map['c2']) == \
        set(['foo'])
    assert set(current_openaire.inverse_openaire_community_map['c3']) == \
        set(['bar'])

    assert set(current_openaire.openaire_communities.keys()) == \
        set(['foo', 'bar'])
