# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Unit tests Zenodo Deposit indexing."""

from __future__ import absolute_import, print_function

from helpers import publish_and_expunge
from invenio_deposit.api import Deposit
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search
from invenio_search.api import RecordsSearch
from six import BytesIO, b

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.records.resolvers import record_resolver


def test_deposit_index(db, es):
    """Test update embargoed records."""
    deposit_index_name = 'deposits-records-record-v1.0.0'
    rec1 = Record.create({
        'title': 'One',
        '_deposit': {
            'status': 'published',
            'pid': {
                'type': 'recid',
                'value': '1'
            }
        }
    })
    PersistentIdentifier.create(pid_type='recid', pid_value='1',
                                status=PIDStatus.REGISTERED,
                                object_uuid=rec1.id, object_type='rec')
    Deposit.create({
        '_deposit': {
            'status': 'published',
            'pid': {
                'type': 'recid',
                'value': '1'
            }
        }
    })
    db.session.commit()
    current_search.flush_and_refresh(deposit_index_name)
    res = RecordsSearch(index=deposit_index_name).execute()
    # Make sure the 'title' was indexed from record
    assert res['hits']['hits'][0]['_source']['title'] == 'One'


def test_versioning_indexing(db, es, deposit, deposit_file):
    """Test the indexing of 'version' relations."""
    deposit_index_name = 'deposits-records-record-v1.0.0'
    records_index_name = 'records-record-v1.0.0'

    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']
    recid_v1, record_v1 = deposit_v1.fetch_published()
    recid_v1_value = recid_v1.pid_value

    RecordIndexer().index_by_id(str(record_v1.id))
    RecordIndexer().process_bulk_queue()
    current_search.flush_and_refresh(index=deposit_index_name)
    current_search.flush_and_refresh(index=records_index_name)
    s_dep = RecordsSearch(index=deposit_index_name).execute()['hits']['hits']
    s_rec = RecordsSearch(index=records_index_name).execute()['hits']['hits']

    assert len(s_dep) == 1
    assert len(s_rec) == 1
    assert 'relations' in s_dep[0]['_source']
    assert 'relations' in s_rec[0]['_source']

    expected = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 0,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "2"
                },
                "count": 1,
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }
    assert s_dep[0]['_source']['relations'] == expected
    assert s_rec[0]['_source']['relations'] == expected

    deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.object_uuid)
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)

    RecordIndexer().process_bulk_queue()
    current_search.flush_and_refresh(index=deposit_index_name)
    current_search.flush_and_refresh(index=records_index_name)
    s_dep = RecordsSearch(index=deposit_index_name).execute()['hits']['hits']
    s_rec = RecordsSearch(index=records_index_name).execute()['hits']['hits']

    assert len(s_dep) == 2  # Two deposits should be indexed
    assert len(s_rec) == 1  # One, since record does not exist yet

    s_dep1 = current_search.client.get(
        index=deposit_index_name, id=deposit_v1.id)
    s_dep2 = current_search.client.get(
        index=deposit_index_name, id=deposit_v2.id)

    expected_d1 = {
        "version": [
            {
                "draft_child_deposit": {
                    "pid_type": "depid",
                    "pid_value": "3"
                },
                "index": 0,
                "is_last": False,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "2"
                },
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
                "count": 2  # For deposit, draft children are also counted
            }
        ]
    }
    expected_d2 = {
        "version": [
            {
                "draft_child_deposit": {
                    "pid_type": "depid",
                    "pid_value": "3"
                },
                "index": 1,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "2"
                },
                "count": 2,  # For deposit, draft children are also counted
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }

    assert s_dep1['_source']['relations'] == expected_d1
    assert s_dep2['_source']['relations'] == expected_d2

    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)

    RecordIndexer().index_by_id(str(record_v2.id))
    RecordIndexer().process_bulk_queue()
    current_search.flush_and_refresh(index=deposit_index_name)
    current_search.flush_and_refresh(index=records_index_name)

    s_dep = RecordsSearch(index=deposit_index_name).execute()['hits']['hits']
    s_rec = RecordsSearch(index=records_index_name).execute()['hits']['hits']
    assert len(s_dep) == 2
    assert len(s_rec) == 2

    s_dep1 = current_search.client.get(
        index=deposit_index_name, id=deposit_v1.id)
    s_dep2 = current_search.client.get(
        index=deposit_index_name, id=deposit_v2.id)

    s_rec1 = current_search.client.get(
        index=records_index_name, id=record_v1.id)
    s_rec2 = current_search.client.get(
        index=records_index_name, id=record_v2.id)

    expected_d1 = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 0,
                "is_last": False,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
                "count": 2
            }
        ]
    }
    expected_d2 = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 1,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "count": 2,
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }
    assert s_dep1['_source']['relations'] == expected_d1
    assert s_dep2['_source']['relations'] == expected_d2

    expected_r1 = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 0,
                "is_last": False,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
                "count": 2
            }
        ]
    }
    expected_r2 = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 1,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "count": 2,
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }
    assert s_rec1['_source']['relations'] == expected_r1
    assert s_rec2['_source']['relations'] == expected_r2
