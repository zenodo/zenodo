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

"""Test validation in Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import json

from invenio_search import current_search


def get_data(**kwargs):
    """Get test data."""
    test_data = dict(
        metadata=dict(
            upload_type='presentation',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
                dict(name='Smith, Jane', affiliation='Atlantis')
            ],
            description='Test Description',
            publication_date='2013-05-08',
            access_right='open'
        )
    )
    test_data['metadata'].update(kwargs)
    return test_data


def test_missing_files(api, api_client, deposit, oauth2_headers_user_1,
                       deposit_url, get_json):
    """Test data validation."""
    client = api_client
    headers = oauth2_headers_user_1

    # Create
    res = client.post(
        deposit_url, data=json.dumps(get_data()), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Publish - not possible (file is missing)
    res = client.post(links['publish'], headers=headers)
    data = get_json(res, code=400)
    print(data)
    assert len(data['errors']) == 1
