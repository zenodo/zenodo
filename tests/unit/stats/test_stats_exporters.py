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

"""Unit tests for statistics exporters."""
from datetime import datetime, timedelta

import pytest
from invenio_cache import current_cache
from mock import mock
from stats_helpers import create_stats_fixtures

from zenodo.modules.stats.exporters import PiwikExporter, \
    PiwikExportRequestError


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = status_code == 200

    def json(self):
        return self.json_data


def mocked_requests_success(*args, **kwargs):
    json = {'status': 'success', 'invalid': 0}
    return MockResponse(json, 200)


def mocked_requests_invalid(*args, **kwargs):
    json = {'status': 'success', 'invalid': 1}
    return MockResponse(json, 200)


def mocked_requests_fail(*args, **kwargs):
    return MockResponse({}, 500)


@mock.patch('zenodo.modules.stats.exporters.requests.post',
            side_effect=mocked_requests_success)
def test_piwik_exporter(app, db, es, locations, event_queues, full_record):
    records = create_stats_fixtures(
        metadata=full_record, n_records=1, n_versions=1, n_files=1,
        event_data={'user_id': '1', 'country': 'CH'},
        # 4 event timestamps
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30),
        do_process_events=True,
        do_aggregate_events=False,
        do_update_record_statistics=False
    )

    current_cache.delete('piwik_export:bookmark')
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark is None

    start_date = datetime(2018, 1, 1, 12)
    end_date = datetime(2018, 1, 1, 14)
    PiwikExporter().run(start_date=start_date, end_date=end_date)
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark == u'2018-01-01T14:00:00'

    PiwikExporter().run()
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark == u'2018-01-01T14:30:00'


@mock.patch('zenodo.modules.stats.exporters.requests.post',
            side_effect=mocked_requests_invalid)
def test_piwik_exporter_invalid_request(app, db, es, locations, event_queues,
                                        full_record):
    records = create_stats_fixtures(
        metadata=full_record, n_records=1, n_versions=1, n_files=1,
        event_data={'user_id': '1', 'country': 'CH'},
        # 4 event timestamps
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30),
        do_process_events=True)

    current_cache.delete('piwik_export:bookmark')
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark is None

    PiwikExporter().run()
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark is None


@mock.patch('zenodo.modules.stats.exporters.requests.post',
            side_effect=mocked_requests_fail)
def test_piwik_exporter_request_fail(app, db, es, locations, event_queues,
                                     full_record):
    records = create_stats_fixtures(
        metadata=full_record, n_records=1, n_versions=1, n_files=1,
        event_data={'user_id': '1', 'country': 'CH'},
        # 4 event timestamps
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30),
        do_process_events=True)

    current_cache.delete('piwik_export:bookmark')
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark is None

    with pytest.raises(PiwikExportRequestError):
        PiwikExporter().run()
    bookmark = current_cache.get('piwik_export:bookmark')
    assert bookmark is None
