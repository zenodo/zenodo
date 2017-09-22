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

"""Test Zenodo deposit utils."""

from __future__ import absolute_import, print_function

from zenodo.modules.deposit.utils import suggest_language


def test_suggest_language():
    """Test language suggestions."""
    s = suggest_language('pl')
    assert len(s) == 1
    assert s[0].alpha_3 == 'pol'
    # 'Northern Sami' doesn't contain 'sme' substring but should be first
    # in suggestions, since 'sme' is its ISO 639-2 code.
    s = suggest_language('sme')
    assert len(s) > 1  # More than one result
    assert s[0].alpha_3 == 'sme'
    assert 'sme' not in s[0].name.lower()
    assert 'sme' in s[1].name.lower()  # Second result matched by name

    s = suggest_language('POLISH')
    assert s[0].alpha_3 == 'pol'

    # lower-case
    s = suggest_language('polish')
    assert s[0].alpha_3 == 'pol'
