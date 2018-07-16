# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo JSON schema tests."""

from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from mock import patch

from zenodo.modules.records.serializers import json_v1


def test_json_v1(app, db, minimal_record, recid_pid):
    """Test json_v1."""
    stats = {
        'version_views': 312, 'views': 213,
        'version_downloads': 54, 'downloads': 28,
        'version_volume': 213000, 'volume': 2000,
        'version_unique_views': 280, 'unique_views': 27,
        'version_unique_downloads': 280, 'unique_download': 27
    }

    with patch('zenodo.modules.records.serializers.schemas.json.get_record_stats',
               return_value=stats) as m:
        obj = json_v1.transform_record(recid_pid,
                                       Record.create(minimal_record))
        assert m.called
        assert obj['stats'] == stats


def test_record_stats_serialization(app_client, db, minimal_record):
    """Test record stats serialization."""
    record = Record.create(minimal_record)
    record['_stats'] = {}
    pid = PersistentIdentifier.create(
        'recid', '12345', object_type='rec', object_uuid=record.id,
        status=PIDStatus.REGISTERED)
    db.session.commit()
    db.session.refresh(pid)

    RecordIndexer().index_by_id(record.id)

    search_url = '/search'
    with patch('zenodo.modules.records.serializers.schemas.json.get_record_stats') as m:
        res = app_client.get(search_url)
        assert not m.called
