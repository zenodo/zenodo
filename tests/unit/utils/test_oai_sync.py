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

"""Test API for Zenodo and GitHub integration."""

from __future__ import absolute_import, print_function

from invenio_oaiserver.models import OAISet
from mock import MagicMock, patch

from zenodo.modules.utils.tasks import comm_sets_match, get_synced_sets, \
    requires_sync, update_oaisets_cache


def make_rec(comm, sets):
    """Create a minimal record for Community-OAISet testing."""
    return {'communities': comm, '_oai': {'sets': sets}}


def test_synced_communities(db, oaisets):
    """Test OAI sets syncing."""
    assert get_synced_sets(make_rec(['c1', 'c2'],
                                    ['user-c1', 'user-c2'])) == \
        ['user-c1', 'user-c2']
    assert get_synced_sets(make_rec(['c1', 'c2'], [])) == \
        ['user-c1', 'user-c2']
    assert get_synced_sets(make_rec(['c1', 'c2'],
                                    ['extra', 'user-c1', 'user-c2'])) == \
        ['extra', 'user-c1', 'user-c2']

    assert get_synced_sets(make_rec(['c1', 'c2'],
                                    ['user-c1', 'user-c2', 'user-extra'])) == \
        ['user-c1', 'user-c2', 'user-extra']
    assert get_synced_sets(make_rec([], ['extra'])) == ['extra']
    assert get_synced_sets(make_rec([], [])) == []
    assert get_synced_sets({}) == []


def test_sets_match(db, oaisets):
    """Test OAI sets and communities matching predicate."""
    # Should ignore the custom "extra" OAI Set
    assert comm_sets_match(make_rec(['c1', 'c2'],
                                    ['extra', 'user-c1', 'user-c2', ]))
    # Should also ignore the custom "user-extra" spec which is NOT
    # community-based but has a prefix as such
    assert comm_sets_match(make_rec(['c1', 'c2'],
                                    ['user-c1', 'user-c2', 'user-extra', ]))
    assert comm_sets_match(make_rec([], ['extra']))
    assert comm_sets_match(make_rec([], []))
    assert not comm_sets_match(make_rec(['c2'], ['extra']))
    assert not comm_sets_match(make_rec(['c2'], ['user-c1']))
    assert not comm_sets_match(make_rec(['c1'], []))
    r = {
        'communities': ['c1'],
        '_oai': {
            'id': 'some_id_1234',
            'updated': 'timestamp'
        }
    }
    assert not comm_sets_match(r)


def test_syncing_required(db, oaisets):
    """Test OAI syncing requirement criterion."""
    assert requires_sync({})
    r = {
        'communities': ['c1', ],
        '_oai': {
            'id': 'some_id_1234',
            'updated': 'timestamp',
            'sets': ['user-c1', 'extra', ]
        }
    }
    assert not requires_sync(r)  # should not update it

    r = {
        'communities': ['c1', ],
        '_oai': {
            # 'id' is missing
            'updated': 'timestamp',
            'sets': ['user-c1', 'extra', ]
        }
    }
    assert requires_sync(r)

    r = {
        'communities': ['c1', ],
        '_oai': {
            'id': '',  # 'id' empty
            'updated': 'timestamp',
            'sets': ['user-c1', 'extra', ]
        }
    }
    assert requires_sync(r)

    r = {
        'communities': ['c1', ],
        '_oai': {
            'id': 'some_id_1234',
            # update is missing
            'sets': ['user-c1', 'extra', ]
        }
    }
    assert requires_sync(r)

    r = {
        'communities': ['c1', ],
        '_oai': {
            'id': 'some_id_1234',
            'updated': 'timestamp',
            'sets': ['extra', 'user-c2', ]  # additional 'user-c2'
        }
    }
    assert requires_sync(r)

    r = {
        'communities': ['c1', 'c2'],
        '_oai': {
            'id': 'some_id_1234',
            'updated': 'timestamp',
            'sets': ['extra', 'user-c1', ]  # 'user-c2' missing
        }
    }
    assert requires_sync(r)  # should not update it

    r = {
        'communities': ['c1', ],
        '_oai': {
            'id': 'some_id_1234',
            'updated': 'timestamp',
            # sets missing
        }
    }
    assert requires_sync(r)  # should not update it

    r = {
        'communities': ['c1', ],
        # _oai is missing completely
    }
    assert requires_sync(r)  # should not update it


def test_sets_cache(db, oaisets):
    """Test caching for OAISets."""
    cache = {}
    rec = {
        '_oai': {
            'sets': ['user-c1', 'extra', ],
        }
    }
    update_oaisets_cache(cache, rec)
    assert cache['user-c1'].search_pattern is None
    assert cache['extra'].search_pattern == 'title:extra'  # see in conftest

    with patch.object(OAISet, 'query') as query_mock:
        # Mock the sqlalchemy query API
        q_result_mock = MagicMock()
        q_result_mock.count = 1
        q_result_mock.one().search_pattern = None
        query_mock.filter_by = MagicMock(return_value=q_result_mock)
        r = {
            'communities': ['c1', 'c2'],
            '_oai': {
                'id': 'some_id_1234',
                'updated': 'timestamp',
                'sets': ['user-c1', 'extra', 'user-c2']
            }
        }
        assert not requires_sync(r, cache=cache)  # Should not require sync
        # Should be only called once for the item not in cache
        query_mock.filter_by.assert_called_once_with(spec='user-c2')
