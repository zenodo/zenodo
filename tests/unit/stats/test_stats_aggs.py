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

"""Unit tests statistics aggregations."""

from datetime import datetime, timedelta

from elasticsearch_dsl import Search
from invenio_search.api import RecordsSearch
from stats_helpers import create_stats_fixtures

from elasticsearch_dsl.query import Ids


def test_basic_stats(app, db, es, locations, event_queues, minimal_record):
    """Test basic statistics results."""
    search = Search(using=es)
    records = create_stats_fixtures(
        # (10 * 2) -> 20 records and (10 * 2 * 3) -> 60 files
        metadata=minimal_record, n_records=10, n_versions=2, n_files=3,
        event_data={'user_id': '1'},
        # 4 event timestamps
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30))

    # Events indices
    prefix = app.config['SEARCH_INDEX_PREFIX']

    # 2 versions * 10 records * 3 files * 4 events -> 240
    assert search.index(prefix + 'events-stats-file-download').count() == 240
    # 2 versions * 10 records * 4 events -> 80
    assert search.index(prefix + 'events-stats-record-view').count() == 80

    # Aggregations indices
    # (2 versions + 1 concept) * 10 records -> 30 documents + 2 bookmarks

    # 30d
    assert search.index(prefix + 'stats-file-download').count() == 30

    # 30d
    assert search.index(prefix + 'stats-record-view').count() == 30

    # 2bm + 2bm
    assert search.index(prefix + 'bookmark-index').count() == 4

    # Records index
    for _, record, _ in records:
        query = search.index(prefix + '*') \
            .query(Ids(values=[str(record.id)])) \
            .source(include='_stats')

        doc = (query.execute()[0])
        assert doc['_stats'] == {
            # 4 view events
            'views': 4.0, 'version_views': 8.0,
            # 4 view events over 2 different hours
            'unique_views': 2.0, 'version_unique_views': 2.0,
            # 4 download events * 3 files
            'downloads': 12.0, 'version_downloads': 24.0,
            # 4 download events * 3 files over 2 different hours
            'unique_downloads': 2.0, 'version_unique_downloads': 2.0,
            # 4 download events * 3 files * 10 bytes
            'volume': 120.0, 'version_volume': 240.0,
        }


def test_large_stats(app, db, es, locations, event_queues, minimal_record):
    """Test record page view event import."""
    search = Search(using=es)
    records = create_stats_fixtures(
        # (3 * 4) -> 12 records and (3 * 4 * 2) -> 24 files
        metadata=minimal_record, n_records=3, n_versions=4, n_files=2,
        event_data={'user_id': '1'},
        # (31 + 30) * 2 -> 122 event timestamps (61 days and 2 events/day)
        start_date=datetime(2018, 3, 1),
        end_date=datetime(2018, 5, 1),
        interval=timedelta(hours=12))

    # Events indices
    prefix = app.config['SEARCH_INDEX_PREFIX']

    # 4 versions * 3 records * 2 files * 122 events -> 2928
    assert search.index(prefix + 'events-stats-file-download').count() == 2928
    # 4 versions * 3 records * 122 events -> 1464
    assert search.index(prefix + 'events-stats-record-view').count() == 1464

    # Aggregations indices
    # (4 versions + 1 concept) * 3 records -> 15 documents + 2 bookmarks
    q = search.index(prefix + 'stats-file-download')
    q = q.doc_type('file-download-day-aggregation')
    assert q.count() == 915  # 61 days * 15 records
    q = search.index(prefix + 'stats-record-view')
    q = q.doc_type('record-view-day-aggregation')
    assert q.count() == 915  # 61 days * 15 records

    # import wdb; wdb.set_trace()

    # Reords index
    for _, record, _ in records:
        query = search.index(prefix + '*') \
            .query(Ids(values=[str(record.id)])) \
            .source(include='_stats')
        doc = (query.execute()[0])
        assert doc['_stats'] == {
            # 4 view events
            'views': 122.0, 'version_views': 488.0,
            # 4 view events over 2 different hours
            'unique_views': 122.0, 'version_unique_views': 122.0,
            # 4 download events * 3 files
            'downloads': 244.0, 'version_downloads': 976.0,
            # 4 download events * 3 files over 2 different hours
            'unique_downloads': 122.0, 'version_unique_downloads': 122.0,
            # 4 download events * 3 files * 10 bytes
            'volume': 2440.0, 'version_volume': 9760.0,
        }
