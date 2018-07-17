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

from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta
from types import MethodType

from elasticsearch_dsl import Search
from flask import current_app, url_for
from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_files_rest.signals import file_downloaded
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.models import RecordsBuckets
from invenio_records_ui.signals import record_viewed
from invenio_search import current_search
from invenio_search.api import RecordsSearch
from invenio_stats import current_stats
from invenio_stats.tasks import aggregate_events, process_events
from six import BytesIO

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.stats.tasks import update_record_statistics


def _create_records(base_metadata, total, versions, files):
    records = []
    cur_recid = 1
    for _ in range(total):
        conceptrecid = cur_recid
        for ver_idx in range(versions):
            recid = conceptrecid + ver_idx + 1
            data = deepcopy(base_metadata)
            data.update({
                'conceptrecid': str(conceptrecid),
                'conceptdoi': '10.1234/{}'.format(recid),
                'recid': recid,
                'doi': '10.1234/{}'.format(recid),
            })
            record = ZenodoRecord.create(data)
            bucket = Bucket.create()
            RecordsBuckets.create(bucket=bucket, record=record.model)
            pid = PersistentIdentifier.create(
                pid_type='recid', pid_value=record['recid'], object_type='rec',
                object_uuid=record.id, status='R')

            file_objects = []
            for f in range(files):
                filename = 'Test{0}_v{1}.pdf'.format(f, ver_idx)
                record.files[filename] = BytesIO(b'1234567890')  # 10 bytes
                record.files[filename]['type'] = 'pdf'
                file_objects.append(record.files[filename].obj)
            record.commit()

            db.session.commit()
            records.append((pid, record, file_objects))
        cur_recid += versions + 1
    return records


def _gen_date_range(start, end, interval):
    assert isinstance(interval, timedelta)
    cur_date = start
    while cur_date < end:
        yield cur_date
        cur_date += interval


def _create_and_process_events(metadata, n_records, n_versions, n_files,
                               event_data, start_date, end_date, interval):
    records = _create_records(
        metadata, total=n_records, versions=n_versions, files=n_files)

    @contextmanager
    def _patch_stats_publish():
        original_publish = current_stats.publish

        event_batches = defaultdict(list)

        def _patched_publish(self, event_type, events):
            events[0].update(event_data)
            event_batches[event_type].append(events[0])
        current_stats.publish = MethodType(_patched_publish, current_stats)
        yield
        current_stats.publish = original_publish
        for event_type, events in event_batches.items():
            current_stats.publish(event_type, events)

    with _patch_stats_publish():
        for ts in _gen_date_range(start_date, end_date, interval):
            event_data['timestamp'] = ts.isoformat()
            for recid, record, file_objects in records:
                with current_app.test_request_context():
                    record_viewed.send(current_app._get_current_object(),
                                       pid=recid, record=record)
                    for obj in file_objects:
                        file_downloaded.send(
                            current_app._get_current_object(),
                            obj=obj, record=record)
    process_events(['record-view', 'file-download'])
    current_search.flush_and_refresh(index='events-stats-*')

    aggregate_events(
        ['record-view-agg', 'record-view-all-versions-agg',
         'record-download-agg', 'record-download-all-versions-agg'])
    current_search.flush_and_refresh(index='stats-*')

    update_record_statistics(start_date=start_date.isoformat(),
                             end_date=end_date.isoformat())
    RecordIndexer().process_bulk_queue()
    current_search.flush_and_refresh(index='records')

    return records


def test_basic_stats(app, db, es, locations, event_queues, minimal_record):
    """Test basic statistics results."""
    search = Search(using=es)
    records = _create_and_process_events(
        # (10 * 2) -> 20 records and (10 * 2 * 3) -> 60 files
        metadata=minimal_record, n_records=10, n_versions=2, n_files=3,
        event_data={'user_id': '1'},
        # 4 event timestamps
        start_date=datetime(2018, 1, 1, 13),
        end_date=datetime(2018, 1, 1, 15),
        interval=timedelta(minutes=30))
    # Events indices
    # 2 versions * 10 records * 3 files * 4 events -> 240
    assert search.index('events-stats-file-download').count() == 240
    # 2 versions * 10 records * 4 events -> 80
    assert search.index('events-stats-record-view').count() == 80

    # Aggregations indices
    # (2 versions + 1 concept) * 10 records -> 30 documents + 2 bookmarks
    assert search.index('stats-file-download').count() == 32  # 2bm + 30d
    assert search.index('stats-record-view').count() == 32  # 2bm + 30d

    # Reords index
    for _, record, _ in records:
        doc = (
            RecordsSearch().get_record(record.id)
            .source(include='_stats').execute()[0])
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
    records = _create_and_process_events(
        # (3 * 4) -> 12 records and (3 * 4 * 2) -> 24 files
        metadata=minimal_record, n_records=3, n_versions=4, n_files=2,
        event_data={'user_id': '1'},
        # (31 + 30) * 2 -> 122 event timestamps (61 days and 2 events/day)
        start_date=datetime(2018, 3, 1),
        end_date=datetime(2018, 5, 1),
        interval=timedelta(hours=12))

    # Events indices
    # 4 versions * 3 records * 2 files * 122 events -> 2928
    assert search.index('events-stats-file-download').count() == 2928
    # 4 versions * 3 records * 122 events -> 1464
    assert search.index('events-stats-record-view').count() == 1464

    # Aggregations indices
    # (4 versions + 1 concept) * 3 records -> 15 documents + 2 bookmarks
    assert search.index('stats-file-download').count() == 933  # 2bm + 30d
    assert search.index('stats-record-view').count() == 933  # 2bm + 30d

    # Reords index
    for _, record, _ in records:
        doc = (
            RecordsSearch().get_record(record.id)
            .source(include='_stats').execute()[0])
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
