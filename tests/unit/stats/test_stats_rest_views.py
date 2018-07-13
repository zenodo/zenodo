# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Unit tests for stats rest views."""

import json

from helpers import login_user_via_session


def test_queries_permission_factory(app, db, es, event_queues, users,
                                    record_with_files_creation, api_client):
    """Test queries permission factory."""
    recid, record, _ = record_with_files_creation
    record['conceptdoi'] = '10.1234/foo.concept'
    record['conceptrecid'] = 'foo.concept'
    record.commit()
    db.session.commit()

    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    sample_histogram_query_data = {
        "mystat": {
            "stat": "record-download",
            "params": {
                "file_key": "Test.pdf",
                "recid": recid.pid_value
            }
        }
    }
    query_url = '/stats'

    login_user_via_session(api_client, email=users[0]['email'])
    res = api_client.post(query_url, headers=headers,
                          data=json.dumps(sample_histogram_query_data))
    assert res.status_code == 403

    login_user_via_session(api_client, email=users[2]['email'])
    res = api_client.post(query_url, headers=headers,
                          data=json.dumps(sample_histogram_query_data))
    assert res.status_code == 200
