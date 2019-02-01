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

"""Test OpenAIRE community mapping."""

from zenodo.modules.utils.openaire import create_communities,\
    get_new_communites


def get_communities_mapping(user_emails):
    return {
        'oa_comm1': dict(name='Community num 1',
                         communities=[],
                         types=[],
                         primary_community='zenodo',
                         curators=[user_emails[0]]),
        'oa_comm2': dict(name='Community num 2',
                         communities=[],
                         types=[],
                         primary_community='z_comm2',
                         curators=[user_emails[1]]),
    }


def get_new_communities(user_id):
    return [
        dict(id='z_comm2',
             title='Community num 2',
             owner=user_id)
    ]


def test_get_new_communites(db, users, communities):
    """Test get new communities."""
    user_emails = [users[0]['email'], users[1]['email']]
    communities = get_communities_mapping(user_emails)
    new_communities = get_new_communities(users[1]['id'])

    result = get_new_communites(communities)

    assert result == new_communities


def test_create_communities(db, users, communities):
    """Test create community."""
    user_emails = [users[0]['email'], users[1]['email']]
    communities = get_communities_mapping(user_emails)
    new_communities = get_new_communities(users[1]['id'])

    create_communities(new_communities)

    result = get_new_communites(communities)

    assert result == []
