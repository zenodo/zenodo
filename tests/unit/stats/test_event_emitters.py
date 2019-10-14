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

"""Unit tests statistics for record views."""

from elasticsearch_dsl import Search
from flask import url_for
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search
from invenio_stats.tasks import process_events


def test_record_page(app, db, es, event_queues, full_record):
    """Test record page views."""
    full_record['conceptdoi'] = '10.1234/foo.concept'
    full_record['conceptrecid'] = 'foo.concept'
    r = Record.create(full_record)
    PersistentIdentifier.create(
        'recid', '12345', object_type='rec', object_uuid=r.id,
        status=PIDStatus.REGISTERED)
    db.session.commit()

    with app.test_client() as client:
        record_url = url_for('invenio_records_ui.recid', pid_value='12345')
        assert client.get(record_url).status_code == 200

    process_events(['record-view'])
    current_search.flush_and_refresh(index='events-stats-record-view')

    prefix = app.config['SEARCH_INDEX_PREFIX']
    search = Search(using=es, index=prefix+'events-stats-record-view')
    assert search.count() == 1
    doc = search.execute()[0]
    assert doc['doi'] == '10.1234/foo.bar'
    assert doc['conceptdoi'] == '10.1234/foo.concept'
    assert doc['recid'] == '12345'
    assert doc['conceptrecid'] == 'foo.concept'
    assert doc['resource_type'] == {'type': 'publication', 'subtype': 'book'}
    assert doc['access_right'] == 'open'
    assert doc['communities'] == ['zenodo']
    assert doc['owners'] == [1]


def test_file_download(app, db, es, event_queues, record_with_files_creation):
    """Test file download views."""
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

    process_events(['file-download'])
    current_search.flush_and_refresh(index='events-stats-file-download')

    prefix = app.config['SEARCH_INDEX_PREFIX']
    search = Search(using=es, index=prefix+'events-stats-file-download')
    assert search.count() == 1
    doc = search.execute()[0]
    assert doc['doi'] == '10.1234/foo.bar'
    assert doc['conceptdoi'] == '10.1234/foo.concept'
    assert doc['recid'] == '12345'
    assert doc['conceptrecid'] == 'foo.concept'
    assert doc['resource_type'] == {'type': 'publication', 'subtype': 'book'}
    assert doc['access_right'] == 'open'
    assert doc['communities'] == ['zenodo']
    assert doc['owners'] == [1]
