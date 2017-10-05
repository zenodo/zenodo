# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Test Zenodo deposit tasks."""

from __future__ import absolute_import, print_function, unicode_literals

from copy import deepcopy

import datacite
import pytest
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.minters import zenodo_record_minter


def test_datacite_register(mocker, app, db, es, minimal_record):
    dc_mock = mocker.patch(
        'invenio_pidstore.providers.datacite.DataCiteMDSClient')
    doi_tags = [
        '<identifier identifierType="DOI">{doi}</identifier>',
        ('<relatedIdentifier relatedIdentifierType="DOI" '
         'relationType="IsPartOf">{conceptdoi}</relatedIdentifier>'),
    ]
    conceptdoi_tags = [
        '<identifier identifierType="DOI">{conceptdoi}</identifier>',
    ]
    has_part_tag = ('<relatedIdentifier relatedIdentifierType="DOI" '
                    'relationType="HasPart">{doi}</relatedIdentifier>')

    # Assert calls and content
    def assert_datacite_calls_and_content(record, doi_tags, conceptdoi_tags):
        """Datacite client calls assertion helper."""
        assert dc_mock().metadata_post.call_count == 2
        _, doi_args, _ = dc_mock().metadata_post.mock_calls[0]
        _, conceptdoi_args, _ = dc_mock().metadata_post.mock_calls[1]
        assert all([t.format(**record) in doi_args[0] for t in doi_tags])
        assert all([t.format(**record) in conceptdoi_args[0]
                    for t in conceptdoi_tags])

        dc_mock().doi_post.call_count == 2
        dc_mock().doi_post.assert_any_call(
            record['doi'],
            'https://zenodo.org/record/{}'.format(record['recid']))
        dc_mock().doi_post.assert_any_call(
            record['conceptdoi'],
            'https://zenodo.org/record/{}'.format(record['conceptrecid']))

    # Create conceptrecid for the records
    conceptrecid = PersistentIdentifier.create(
        'recid', '100', status=PIDStatus.RESERVED)

    def create_versioned_record(recid_value, conceptrecid):
        """Utility function for creating versioned records."""
        recid = PersistentIdentifier.create(
            'recid', recid_value, status=PIDStatus.RESERVED)
        pv = PIDVersioning(parent=conceptrecid)
        pv.insert_draft_child(recid)

        record_metadata = deepcopy(minimal_record)
        record_metadata['conceptrecid'] = conceptrecid.pid_value
        record_metadata['recid'] = int(recid.pid_value)
        record = ZenodoRecord.create(record_metadata)
        zenodo_record_minter(record.id, record)
        record.commit()

        return recid, record

    # Create a reserved recid
    recid1, r1 = create_versioned_record('101', conceptrecid)
    db.session.commit()

    datacite_register(recid1.pid_value, str(r1.id))

    conceptdoi_tags.append(has_part_tag.format(**r1))
    assert_datacite_calls_and_content(r1, doi_tags, conceptdoi_tags)

    # Create a new version
    recid2, r2 = create_versioned_record('102', conceptrecid)
    db.session.commit()

    dc_mock().reset_mock()
    datacite_register(recid2.pid_value, str(r2.id))

    conceptdoi_tags.append(has_part_tag.format(**r2))
    assert_datacite_calls_and_content(r2, doi_tags, conceptdoi_tags)


def test_datacite_register_fail(mocker, app, db, es, minimal_record):
    # Make the datacite API unavailable
    dc_mock = mocker.patch(
        'invenio_pidstore.providers.datacite.DataCiteMDSClient')
    dc_mock().metadata_post.side_effect = datacite.errors.HttpError()

    # Create a reserved recid
    record = Record.create(minimal_record)
    record_uuid = record.id
    recid = record['recid']
    recid_pid = PersistentIdentifier.create(
        'recid', recid, status=PIDStatus.RESERVED)

    # Mint the record
    zenodo_record_minter(record_uuid, record)
    record.commit()
    db.session.commit()

    with pytest.raises(datacite.errors.HttpError):
        datacite_register.apply((recid_pid.pid_value, str(record_uuid)))

    # Check that the task was retried ("max_retries" + 1) times
    dc_calls = len(dc_mock().metadata_post.mock_calls)
    assert dc_calls == datacite_register.max_retries + 1
