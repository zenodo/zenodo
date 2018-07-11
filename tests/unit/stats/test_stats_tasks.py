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

from elasticsearch_dsl import Search
from flask import url_for
from invenio_search import current_search
from invenio_search.api import RecordsSearch

from invenio_stats.tasks import aggregate_events, process_events
from zenodo.modules.stats.tasks import update_record_statistics
from invenio_indexer.api import RecordIndexer


def test_record_stats(app, db, es, event_queues, record_with_files_creation):
    """Test record page view event import."""
    search = Search(using=es)
    recid, record, _ = record_with_files_creation
    record['conceptdoi'] = '10.1234/foo.concept'
    record['conceptrecid'] = 'foo.concept'
    record.commit()
    db.session.commit()

    with app.test_client() as client:
        file_url = url_for(
            'invenio_records_ui.recid_files',
            pid_value=recid.pid_value,
            filename='Test.pdf',
        )
        assert client.get(file_url).status_code == 200
        record_url = url_for(
            'invenio_records_ui.recid', pid_value=recid.pid_value)
        assert client.get(record_url).status_code == 200

    process_events(['record-view', 'file-download'])

    current_search.flush_and_refresh(index='events-stats-*')
    assert search.index('events-stats-file-download').count() == 1
    assert search.index('events-stats-record-view').count() == 1

    aggregate_events(
        ['record-view-agg', 'record-view-all-versions-agg',
         'record-download-agg', 'record-download-all-versions-agg'])

    current_search.flush_and_refresh(index='stats-*')
    downloads_alias = search.index('stats-file-download')
    downloads_docs = downloads_alias.doc_type('file-download-day-aggregation')
    views_alias = search.index('stats-record-view')
    views_docs = views_alias.doc_type('record-view-day-aggregation')

    assert downloads_alias.count() == 4  # 2 bookmarks + 2 docs
    assert downloads_docs.count() == 2
    assert views_alias.count() == 4  # 2 bookmarks + 2 docs
    assert views_docs.count() == 2

    update_record_statistics()
    RecordIndexer().process_bulk_queue()

    current_search.flush_and_refresh(index='records')
    doc = RecordsSearch(index='records').get_record(record.id).execute()[0]
    assert doc['_stats'] == {
        'views': 1.0,
        'version_views': 1.0,
        'unique_views': 1.0,
        'version_unique_views': 1.0,
        'downloads': 1.0,
        'version_downloads': 1.0,
        'unique_downloads': 1.0,
        'version_unique_downloads': 1.0,
        'volume': 2.0,
        'version_volume': 2.0,
    }
