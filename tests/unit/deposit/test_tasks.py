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

from __future__ import absolute_import, print_function

import datacite
import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from mock import patch

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.records.minters import zenodo_record_minter


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_datacite_register(dc_mock, app, db, es, minimal_record):
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

    datacite_register(recid_pid.pid_value, str(record_uuid))
    dc_mock().doi_post.assert_called_once_with(
        record['doi'], 'https://zenodo.org/record/{}'.format(recid))


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_datacite_register_fail(dc_mock, app, db, es, minimal_record):
    # Make the datacite API unavailable
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
