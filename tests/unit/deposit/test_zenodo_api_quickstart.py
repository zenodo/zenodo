# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo deposit Quckstart."""

from __future__ import absolute_import, print_function

import json

from flask import url_for
from invenio_search import current_search
from six import BytesIO


def test_zenodo_quickstart_workflow(api, db, es, location, write_token,
                                    oauth2_headers_user_1):
    """Test zenodo quickstart workflow."""
    with api.test_request_context():
        with api.test_client() as client:
            # Try get deposits as anonymous user
            res = client.get(url_for('invenio_deposit_rest.depid_list'))
            assert res.status_code == 401

            # Try get deposits as logged-in user
            res = client.get(
                url_for('invenio_deposit_rest.depid_list'),
                headers=oauth2_headers_user_1
            )
            assert res.status_code == 200
            data = json.loads(res.get_data(as_text=True))
            assert data == []

            # Create a new deposit
            res = client.post(
                url_for('invenio_deposit_rest.depid_list'),
                headers=oauth2_headers_user_1,
                data=json.dumps({})
            )
            assert res.status_code == 201
            data = json.loads(res.get_data(as_text=True))
            deposit_id = data['id']
            assert data['files'] == []
            assert data['title'] == ''
            assert 'created' in data
            assert 'modified' in data
            assert 'id' in data
            assert 'metadata' in data
            assert data['state'] == 'unsubmitted'
            assert data['owner'] == write_token['token'].user_id

            current_search.flush_and_refresh(index='deposits')

            # Upload a file
            files = {'file': (BytesIO(b'1, 2, 3'), "myfirstfile.csv"),
                     'name': 'myfirstfile.csv'}
            res = client.post(
                data['links']['files'],
                headers=oauth2_headers_user_1,
                data=files,
                content_type='multipart/form-data',
            )
            assert res.status_code == 201
            data = json.loads(res.get_data(as_text=True))
            assert data['checksum'] == 'md5:66ce05ea43c73b8e33c74c12d0371bc9'
            assert data['filename'] == 'myfirstfile.csv'
            assert data['filesize'] == 7
            assert data['id']

            # modify deposit
            deposit = {
                "metadata": {
                    "title": "My first upload",
                    "upload_type": "poster",
                    "description": "This is my first upload",
                    "creators": [
                        {
                            "name": "Doe, John",
                            "affiliation": "Zenodo"
                        }
                    ]
                }
            }
            res = client.put(
                url_for(
                    'invenio_deposit_rest.depid_item', pid_value=deposit_id),
                headers=oauth2_headers_user_1,
                data=json.dumps(deposit)
            )
            assert res.status_code == 200

            # Publish deposit
            res = client.post(
                url_for('invenio_deposit_rest.depid_actions',
                        pid_value=deposit_id, action='publish'),
                headers=oauth2_headers_user_1,
            )
            assert res.status_code == 202

            # Check that record exists.
            recid = json.loads(res.get_data(as_text=True))['record_id']
            res = client.get(url_for(
                'invenio_records_rest.recid_item', pid_value=recid))
