# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo template tests."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

from zenodo.modules.records.models import AccessRight, ObjectType


def test_access_right():
    """Test basic access right features."""
    for val in ['open', 'embargoed', 'restricted', 'closed']:
        assert getattr(AccessRight, val.upper()) == val
        assert AccessRight.is_valid(val)

    assert not AccessRight.is_valid('invalid')

    assert AccessRight.as_title(AccessRight.OPEN) == 'Open Access'
    assert AccessRight.as_category(AccessRight.EMBARGOED) == 'warning'

    options = AccessRight.as_options()
    assert isinstance(options, tuple)
    assert options[0] == ('open', 'Open Access')


def test_access_right_embargo():
    """Test access right embargo."""
    assert AccessRight.get(AccessRight.OPEN) == 'open'
    assert AccessRight.get(AccessRight.EMBARGOED) == 'embargoed'
    # Embargo just lifted today.
    today = datetime.utcnow().date()

    assert AccessRight.get(
        AccessRight.EMBARGOED, embargo_date=today) == 'open'
    # Future embargo date.
    assert AccessRight.get(
        AccessRight.EMBARGOED, embargo_date=today+timedelta(days=1)) \
        == 'embargoed'


def test_object_type():
    """Test object type."""
    types = ['publication', 'poster', 'presentation', 'software', 'dataset',
             'image', 'video']

    def _assert_obj(obj):
        assert '$schema' in obj
        assert 'id' in obj
        assert 'internal_id' in obj
        assert 'title' in obj
        assert 'en' in obj['title']
        assert 'title_plural' in obj
        assert 'en' in obj['title_plural']
        assert 'schema.org' in obj
        for c in obj.get('children', []):
            _assert_obj(c)

    for t in types:
        _assert_obj(ObjectType.get(t))

    assert ObjectType.get('invalid') is None
