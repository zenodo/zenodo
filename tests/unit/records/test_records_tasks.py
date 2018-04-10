# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Test Zenodo records tasks."""
import uuid
from copy import deepcopy
from datetime import datetime

from invenio_cache import current_cache
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.minters import zenodo_record_minter
from zenodo.modules.records.tasks import schedule_update_datacite_metadata


def test_datacite_update(mocker, db, minimal_record):
    dc_mock = mocker.patch(
        'invenio_pidstore.providers.datacite.DataCiteMDSClient'
    )

    doi_tags = [
        '<identifier identifierType="DOI">{doi}</identifier>',
        ('<relatedIdentifier relatedIdentifierType="DOI" '
         'relationType="IsVersionOf">{conceptdoi}</relatedIdentifier>'),
    ]

    # Assert calls and content
    def assert_datacite_calls_and_content(record, doi_tags):
        """Datacite client calls assertion helper."""
        assert dc_mock().metadata_post.call_count == 1
        _, doi_args, _ = dc_mock().metadata_post.mock_calls[0]
        assert all([t.format(**record) in doi_args[0] for t in doi_tags])

        assert dc_mock().doi_post.call_count == 1
        dc_mock().doi_post.assert_any_call(
            record['doi'],
            'https://zenodo.org/record/{}'.format(record['recid']))

    def assert_datacite_calls_with_missing_data():
        """Datacite client calls assertion helper."""
        assert dc_mock().metadata_post.call_count == 0
        assert dc_mock().doi_post.call_count == 0

    def create_versioned_record(recid_value, conceptrecid):
        """Utility function for creating versioned records."""
        recid = PersistentIdentifier.create(
            'recid', recid_value, status=PIDStatus.RESERVED)
        pv = PIDVersioning(parent=conceptrecid)
        pv.insert_draft_child(recid)

        record_metadata = deepcopy(minimal_record)
        # Remove the DOI
        del record_metadata['doi']
        record_metadata['conceptrecid'] = conceptrecid.pid_value
        record_metadata['recid'] = int(recid.pid_value)
        record = ZenodoRecord.create(record_metadata)
        zenodo_record_minter(record.id, record)
        record.commit()

        return recid, record

    # Create conceptrecid for the records
    conceptrecid = PersistentIdentifier.create(
        'recid', '100', status=PIDStatus.RESERVED)

    # Create a reserved recid
    recid1, r1 = create_versioned_record('352543', conceptrecid)

    # no registered local DOIs
    schedule_update_datacite_metadata(1)
    assert_datacite_calls_with_missing_data()

    doi_pids = PersistentIdentifier.query.filter(
        PersistentIdentifier.pid_value == '10.5072/zenodo.352543')
    doi_pids[0].status = PIDStatus.REGISTERED

    db.session.commit()

    update_date = doi_pids[0].updated

    # no task_details on Redis cache
    schedule_update_datacite_metadata(1)
    assert_datacite_calls_with_missing_data()
    new_update_date1 = doi_pids[0].updated
    assert update_date == new_update_date1

    task_details = dict(
        job_id=str(uuid.uuid4()),
        from_date=datetime(2015, 1, 1, 13, 33),
        until_date=datetime(2016, 1, 1, 13, 33),
        last_update=datetime.utcnow()
    )
    current_cache.set('update_datacite:task_details', task_details)

    # no registered local DOIs updated inside the interval
    schedule_update_datacite_metadata(1)
    assert_datacite_calls_with_missing_data()
    new_update_date2 = doi_pids[0].updated
    assert update_date == new_update_date2

    task_details = dict(
        job_id=str(uuid.uuid4()),
        from_date=datetime(2015, 1, 1, 13, 33),
        until_date=datetime.utcnow(),
        last_update=datetime.utcnow()
    )
    current_cache.set('update_datacite:task_details', task_details)

    schedule_update_datacite_metadata(1)
    new_update_date3 = doi_pids[0].updated
    assert update_date < new_update_date3

    assert_datacite_calls_and_content(r1, doi_tags)
