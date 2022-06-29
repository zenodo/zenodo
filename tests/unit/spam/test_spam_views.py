# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2022 CERN.
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

"""Test spam views."""

from flask import url_for
from helpers import login_user_via_session
from zenodo.modules.spam.models import SafelistEntry
from invenio_search.proxies import current_search


def test_safelist_add_remove(
    app, api, db, use_safelist_config,
    users, published_record, json_headers,
):
    with api.test_request_context():
        search_empty_query = url_for('invenio_records_rest.recid_list')
        search_with_query = url_for(
            'invenio_records_rest.recid_list', q='test')

    with api.test_client() as api_client:
        # Search results for empty query should return nothing since the record
        # is not safelisted
        res = api_client.get(search_empty_query, headers=json_headers)
        assert len(res.json) == 0
        # Search results with a query should return the record always
        res = api_client.get(search_with_query, headers=json_headers)
        assert len(res.json) == 1

    # Add to safelist
    with app.test_client() as client:
        login_user_via_session(client, email=users[2]['email'])  # admin
        res = client.post(
            url_for('zenodo_spam.safelist_add_remove', user_id=1),
            data={
              'action': 'post',
              'next': url_for('invenio_records_ui.recid',
                              pid_value=published_record['recid'])
            },
            follow_redirects=True
        )

        assert 'Added to safelist' in res.get_data()
        assert SafelistEntry.query.get(1) is not None

    with api.test_client() as api_client:
        current_search.flush_and_refresh(index='records')
        # Search results for empty query should return the record since it is
        # now safelisted
        res = api_client.get(search_empty_query, headers=json_headers)
        assert len(res.json) == 1
        # Search results with a query should return the record always
        res = api_client.get(search_with_query, headers=json_headers)
        assert len(res.json) == 1

    # Remove from safelist
    with app.test_client() as client:
        login_user_via_session(client, email=users[2]['email'])  # admin
        res = client.post(
            url_for('zenodo_spam.safelist_add_remove', user_id=1),
            data={
                'action': 'delete',
                'next': url_for('invenio_records_ui.recid',
                                pid_value=published_record['recid']),
            },
            follow_redirects=True
        )

        assert 'Removed from safelist' in res.get_data()
        assert SafelistEntry.query.get(1) is None

    with api.test_client() as api_client:
        current_search.flush_and_refresh(index='records')
        # Search results for empty query should return nothing since the record
        # is now again not safelisted
        res = api_client.get(search_empty_query, headers=json_headers)
        assert len(res.json) == 0
        # Search results with a query should return the record always
        res = api_client.get(search_with_query, headers=json_headers)
        assert len(res.json) == 1
