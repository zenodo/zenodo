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

from invenio_deposit.api import Deposit
from invenio_records.api import Record
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search


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
    res = current_search.client.search(index=deposit_index_name)
    # Make sure the 'title' was indexed from record
    assert res['hits']['hits'][0]['_source']['title'] == 'One'
