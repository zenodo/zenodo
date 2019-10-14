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

"""Unit tests for statistics tasks."""

from datetime import datetime, timedelta

from flask import url_for
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search
from invenio_stats.tasks import aggregate_events, process_events
from stats_helpers import create_stats_fixtures

from zenodo.modules.stats.tasks import update_record_statistics
from zenodo.modules.stats.utils import get_record_stats


def test_update_record_statistics(app, db, es, locations, event_queues,
                                  minimal_record):
    """Test record statistics update task."""
    records = create_stats_fixtures(
        metadata=minimal_record, n_records=1, n_versions=5, n_files=3,
        event_data={'user_id': '1'},
        # 4 event timestamps (half-hours between 13:00-15:00)
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30),
        # This also runs the task we want to test and indexes records.
        do_update_record_statistics=True)

    expected_stats = {
        'views': 4.0,
        'version_views': 20.0,
        'unique_views': 2.0,
        'version_unique_views': 2.0,
        'downloads': 12.0,
        'version_downloads': 60.0,
        'unique_downloads': 2.0,
        'version_unique_downloads': 2.0,
        'volume': 120.0,
        'version_volume': 600.0,
    }

    # Check current stats for all records
    for recid, _, _ in records:
        stats = get_record_stats(recid.object_uuid)
        assert stats == expected_stats

    # Perform a view and all-files download today on the first version
    recid_v1, record_v1, file_objects_v1 = records[0]
    with app.test_client() as client:
        for f in file_objects_v1:
            file_url = url_for('invenio_records_ui.recid_files',
                               pid_value=recid_v1.pid_value, filename=f.key)
            assert client.get(file_url).status_code == 200
        record_url = url_for(
            'invenio_records_ui.recid', pid_value=recid_v1.pid_value)
        assert client.get(record_url).status_code == 200

    process_events(['record-view', 'file-download'])
    current_search.flush_and_refresh(index='events-stats-*')
    aggregate_events(
        ['record-view-agg', 'record-view-all-versions-agg',
         'record-download-agg', 'record-download-all-versions-agg'])
    current_search.flush_and_refresh(index='stats-*')
    update_record_statistics()
    RecordIndexer().process_bulk_queue()
    current_search.flush_and_refresh(index='records')

    # Check current stats for all records
    stats = get_record_stats(recid_v1.object_uuid)
    assert stats == {
        'views': 5.0,
        'version_views': 21.0,
        'unique_views': 3.0,
        'version_unique_views': 3.0,
        'downloads': 15.0,
        'version_downloads': 63.0,
        'unique_downloads': 3.0,
        'version_unique_downloads': 3.0,
        'volume': 150.0,
        'version_volume': 630.0,
    }

    # Other versions will have only their `version_*` statistics updated
    expected_stats['version_views'] += 1
    expected_stats['version_unique_views'] += 1
    expected_stats['version_downloads'] += 3
    expected_stats['version_unique_downloads'] += 1
    expected_stats['version_volume'] += 30
    for recid, _, _ in records[1:]:
        stats = get_record_stats(recid.object_uuid)
        assert stats == expected_stats
