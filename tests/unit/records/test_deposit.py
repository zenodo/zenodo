# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests for deposit."""

from __future__ import absolute_import, print_function

import json

from flask import url_for


def test_deposit_list(api, es):
    """."""

    with api.test_request_context():
        with api.test_client() as client:
            url = url_for('invenio_deposit_rest.dep_list')
            response = client.get(url)
            response_dict = json.loads(response.get_data(as_text=True))
            assert response_dict == {
                'aggregations': {},
                'hits': {
                    'hits': [],
                    'total': 0
                },
                'links': {
                    'self': 'http://localhost/'
                            'deposit/depositions/?q=&page=1&size=10'
                }
            }


def test_deposit_deposition_create(api, es, db):
    """."""

    with api.test_request_context():
        with api.test_client() as client:
            url = url_for('invenio_deposit_rest.dep_list')
            headers = {"Content-Type": "application/json"}
            data = {
                'metadata': {
                    'title': 'My first upload',
                    'upload_type': 'poster',
                    'description': 'This is my first upload',
                    'creators': [
                        {
                            'name': 'Doe, John',
                            'affiliation': 'Zenodo'
                        }
                    ]
                },
                'state': 'done',
                'title': 'Test',
            }
            response = client.post(url, data=json.dumps(data), headers=headers)
            import pytest; pytest.set_trace()
            pass
