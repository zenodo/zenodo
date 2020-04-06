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

"""Statistics testing helpers."""

from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta
from types import MethodType

from flask import current_app
from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_files_rest.signals import file_downloaded
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.models import RecordsBuckets
from invenio_records_ui.signals import record_viewed
from invenio_search import current_search
from invenio_stats import current_stats
from invenio_stats.tasks import aggregate_events, process_events
from mock import patch
from six import BytesIO

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.stats.tasks import update_record_statistics


def mock_date(*date_parts):
    """Mocked 'datetime.utcnow()'."""
    class MockDate(datetime):
        """datetime.datetime mock."""

        @classmethod
        def utcnow(cls):
            """Override to return 'current_date'."""
            return cls(*date_parts)
    return MockDate


def _create_records(base_metadata, total, versions, files):
    records = []
    cur_recid_val = 1
    for _ in range(total):
        conceptrecid_val = cur_recid_val
        conceptrecid = PersistentIdentifier.create(
            'recid', str(conceptrecid_val), status='R')
        db.session.commit()
        versioning = PIDVersioning(parent=conceptrecid)
        for ver_idx in range(versions):
            recid_val = conceptrecid_val + ver_idx + 1
            data = deepcopy(base_metadata)
            data.update({
                'conceptrecid': str(conceptrecid_val),
                'conceptdoi': '10.1234/{}'.format(recid_val),
                'recid': recid_val,
                'doi': '10.1234/{}'.format(recid_val),
            })
            record = ZenodoRecord.create(data)
            bucket = Bucket.create()
            record['_buckets'] = {'record': str(bucket.id)}
            record.commit()
            RecordsBuckets.create(bucket=bucket, record=record.model)
            recid = PersistentIdentifier.create(
                pid_type='recid', pid_value=record['recid'], object_type='rec',
                object_uuid=record.id, status='R')
            versioning.insert_child(recid)

            file_objects = []
            for f in range(files):
                filename = 'Test{0}_v{1}.pdf'.format(f, ver_idx)
                record.files[filename] = BytesIO(b'1234567890')  # 10 bytes
                record.files[filename]['type'] = 'pdf'
                file_objects.append(record.files[filename].obj)
            record.commit()

            db.session.commit()
            records.append((recid, record, file_objects))
        cur_recid_val += versions + 1
    return records


def _gen_date_range(start, end, interval):
    assert isinstance(interval, timedelta)
    cur_date = start
    while cur_date < end:
        yield cur_date
        cur_date += interval


def create_stats_fixtures(metadata, n_records, n_versions, n_files,
                          event_data, start_date, end_date, interval,
                          do_process_events=True, do_aggregate_events=True,
                          do_update_record_statistics=True):
    """Generate configurable statistics fixtures.

    :param dict metadata: Base metadata for the created records.
    :param int n_records: Number of records that will be created.
    :param int n_versions: Number of versions for each record.
    :param int n_files: Number of files for each record version.
    :param dict event_data: Base event metadata (e.g. user, user agent, etc).
    :param datetime start_date: Start date for the generated events.
    :param datetime end_date: End date for the generated events.
    :param timedelta interval: Interval between each group of events.
    :param bool do_process_events: ``True`` will run the ``process_events``
        task.
    :param bool do_aggregate_events: ``True`` will run the ``aggregate_events``
        task.
    :param bool do_update_record_statistics: ``True`` will run the
        ``update_record_statistics`` task.
    """
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
    if do_process_events:
        process_events(['record-view', 'file-download'])
        current_search.flush_and_refresh(index='events-stats-*')

    if do_aggregate_events:
        with patch('invenio_stats.aggregations.datetime',
                   mock_date(*end_date.timetuple()[:3])):
            aggregate_events(
                ['record-view-agg', 'record-view-all-versions-agg',
                 'record-download-agg', 'record-download-all-versions-agg'])
            current_search.flush_and_refresh(index='stats-*')

    if do_update_record_statistics:
        update_record_statistics(start_date=start_date.isoformat(),
                                 end_date=end_date.isoformat())
        RecordIndexer().process_bulk_queue()
        current_search.flush_and_refresh(index='records')

    return records
