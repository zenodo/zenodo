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

"""Test Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

from copy import deepcopy

from flask import url_for
from helpers import publish_and_expunge
from invenio_accounts.testutils import login_user_via_session
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier as PID
from invenio_pidstore.models import PIDStatus
from invenio_records.api import Record
from mock import patch
from six import BytesIO, b

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.utils import delete_record
from zenodo.modules.records.resolvers import record_resolver


def test_deposit_ui_login(app, app_client, deposit, deposit_file, users):
    """Test login on deposit views."""
    with app.test_request_context():
        record_url = url_for(
            'invenio_records_ui.recid', pid_value=deposit['_deposit']['id'])
        delete_url = url_for(
            'zenodo_deposit.delete', pid_value=deposit['_deposit']['id'])
        deposit_url = url_for(
            'invenio_deposit_ui.depid', pid_value=deposit['_deposit']['id'])
        new_url = url_for('invenio_deposit_ui.new')
        index_url = url_for('invenio_deposit_ui.index')

    # Unauthenticated users
    assert app_client.get(index_url).status_code == 302
    assert app_client.get(new_url).status_code == 302
    assert app_client.get(deposit_url).status_code == 302
    assert app_client.get(delete_url).status_code == 302
    deposit.publish()
    assert app_client.get(record_url).status_code == 200
    assert app_client.post(record_url).status_code == 302

    # Login user NOT owner of deposit
    login_user_via_session(app_client, email=users[1]['email'])

    # Can list deposits, create new, and view record.
    assert app_client.get(index_url).status_code == 200
    assert app_client.get(new_url).status_code == 200
    assert app_client.get(record_url).status_code == 200

    # - cannot view deposit or put record in edit mode
    assert app_client.get(deposit_url).status_code == 403
    assert app_client.post(record_url).status_code == 403
    assert app_client.get(delete_url).status_code == 403

    # Login owner of deposit
    login_user_via_session(app_client, email=users[0]['email'])

    # - can view deposit or put record in edit mode
    res = app_client.post(record_url)
    assert res.status_code == 302
    assert 'login' not in res.location
    assert app_client.get(deposit_url).status_code == 200
    assert app_client.get(delete_url).status_code == 403

    login_user_via_session(app_client, email=users[2]['email'])
    # assert app_client.get(delete_url).status_code == 200


def test_tombstone(app, app_client, deposit, deposit_file, users):
    """Test tombstone for edit pages."""
    with app.test_request_context():
        record_url = url_for(
            'invenio_records_ui.recid', pid_value=deposit['_deposit']['id'])
        deposit_url = url_for(
            'invenio_deposit_ui.depid', pid_value=deposit['_deposit']['id'])
        delete_url = url_for(
            'zenodo_deposit.delete', pid_value=deposit['_deposit']['id'])

    deposit.publish()
    recid, record = deposit.fetch_published()
    recid.delete()
    deposit.pid.delete()

    assert app_client.post(record_url).status_code == 302
    assert app_client.get(delete_url).status_code == 302
    assert app_client.get(deposit_url).status_code == 410
    login_user_via_session(app_client, email=users[0]['email'])
    assert app_client.post(record_url).status_code == 410
    assert app_client.get(deposit_url).status_code == 410
    assert app_client.get(delete_url).status_code == 410
    login_user_via_session(app_client, email=users[2]['email'])
    assert app_client.get(delete_url).status_code == 410


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_record_delete(dc_mock, app, db, users, deposit, deposit_file):
    """Delete the record with a single version."""
    deposit = publish_and_expunge(db, deposit)
    recid, record = deposit.fetch_published()
    # Stash a copy of record metadata for later
    rec = deepcopy(record)

    record_uuid = str(record.id)

    assert dc_mock().metadata_delete.call_count == 0

    # users[0] is not an Admin but it doesn't matter in this case.
    delete_record(record.id, 'spam', users[0]['id'])

    # Make sure all PIDs are deleted
    # TODO: oai PID is left registered
    # assert PID.get('oai', rec['_oai']['id']) == PIDStatus.DELETED
    assert PID.get('doi', rec['doi']).status == PIDStatus.DELETED
    assert PID.get('doi', rec['conceptdoi']).status == PIDStatus.DELETED
    assert PID.get('recid', rec['recid']).status == PIDStatus.DELETED
    assert PID.get('recid', rec['conceptrecid']).status == PIDStatus.DELETED
    assert PID.get('depid', rec['_deposit']['id']).status == PIDStatus.DELETED

    assert dc_mock().metadata_delete.call_count == 2
    dc_mock().metadata_delete.assert_any_call('10.5072/zenodo.1')
    dc_mock().metadata_delete.assert_any_call('10.5072/zenodo.2')
    record = Record.get_record(record_uuid)
    assert record['removed_by'] == users[0]['id']
    assert record['removal_reason'] == 'Spam record, removed by Zenodo staff.'


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_record_delete_v1(dc_mock, app, db, users, deposit, deposit_file):
    """Delete a record with multiple versions."""
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit.fetch_published()
    recid_v1_value = recid_v1.pid_value
    deposit_v1.newversion()
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)

    # Stash a copy of v1 for later
    rec1 = deepcopy(record_v1)
    rec1_id = str(record_v1.id)

    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    # Stash a copy of v2 for later
    rec2 = deepcopy(record_v2)

    assert dc_mock().metadata_delete.call_count == 0

    # Remove the first version
    delete_record(rec1_id, 'spam', users[0]['id'])

    # Make sure all PIDs are deleted
    assert PID.get('doi', rec1['doi']).status == PIDStatus.DELETED
    assert PID.get('doi', rec1['conceptdoi']).status == PIDStatus.REGISTERED
    assert PID.get('recid', rec1['recid']).status == PIDStatus.DELETED

    # Make sure conceptrecid is redirecting to v2 (as before)
    crecid = PID.get('recid', rec1['conceptrecid'])
    assert crecid.get_redirect() == PID.get('recid', rec2['recid'])
    assert crecid.status == PIDStatus.REDIRECTED
    assert PID.get('depid', rec1['_deposit']['id']).status == PIDStatus.DELETED

    # Make sure the v2 PIDs are kept intact
    assert PID.get('oai', rec2['_oai']['id']).status == PIDStatus.REGISTERED
    assert PID.get('doi', rec2['doi']).status == PIDStatus.REGISTERED
    assert PID.get('recid', rec2['recid']).status == PIDStatus.REGISTERED
    assert PID.get('depid', rec2['_deposit']['id']).status == \
        PIDStatus.REGISTERED

    # Only the v1 DOI should be deleted
    assert dc_mock().doi_post.call_count == 2
    assert dc_mock().doi_post.has_any_call('10.5072/zenodo.3')
    assert dc_mock().doi_post.has_any_call('10.5072/zenodo.1')
    assert dc_mock().metadata_delete.call_count == 1
    dc_mock().metadata_delete.assert_any_call('10.5072/zenodo.2')
    record = Record.get_record(rec1_id)
    assert record['removed_by'] == users[0]['id']
    assert record['removal_reason'] == 'Spam record, removed by Zenodo staff.'


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_record_delete_v2(dc_mock, app, db, users, deposit, deposit_file):
    """Delete a record (only last version) with multiple versions."""
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit.fetch_published()
    recid_v1_value = recid_v1.pid_value
    deposit_v1.newversion()
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)

    # Stash a copy of v1 for later
    rec1 = deepcopy(record_v1)

    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    # Stash a copy of v2 for later
    rec2 = deepcopy(record_v2)
    rec2_id = str(record_v2.id)

    assert dc_mock().metadata_delete.call_count == 0

    # Remove the first version
    delete_record(rec2_id, 'spam', users[0]['id'])

    # Make sure all PIDs are deleted
    assert PID.get('doi', rec2['doi']).status == PIDStatus.DELETED
    assert PID.get('recid', rec2['recid']).status == PIDStatus.DELETED
    assert PID.get('depid', rec2['_deposit']['id']).status == PIDStatus.DELETED

    # Concept DOI should be left registered
    assert PID.get('doi', rec2['conceptdoi']).status == PIDStatus.REGISTERED

    # Make sure conceptrecid is redirecting to v1
    crecid = PID.get('recid', rec2['conceptrecid'])
    assert crecid.status == PIDStatus.REDIRECTED
    assert crecid.get_redirect() == PID.get('recid', rec1['recid'])

    # Make sure the v1 PIDs are kept intact
    assert PID.get('oai', rec1['_oai']['id']).status == PIDStatus.REGISTERED
    assert PID.get('doi', rec1['doi']).status == PIDStatus.REGISTERED
    assert PID.get('recid', rec1['recid']).status == PIDStatus.REGISTERED
    assert PID.get('depid', rec1['_deposit']['id']).status == \
        PIDStatus.REGISTERED

    # Only the v1 DOI should be deleted
    assert dc_mock().doi_post.call_count == 2
    assert dc_mock().doi_post.has_any_call('10.5072/zenodo.2')
    assert dc_mock().doi_post.has_any_call('10.5072/zenodo.1')
    assert dc_mock().metadata_delete.call_count == 1
    dc_mock().metadata_delete.assert_any_call('10.5072/zenodo.3')
    record = Record.get_record(rec2_id)
    assert record['removed_by'] == users[0]['id']
    assert record['removal_reason'] == 'Spam record, removed by Zenodo staff.'


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_record_delete_legacy(dc_mock, app, db, users, deposit, deposit_file):
    """Delete the non-versioned record."""
    deposit = publish_and_expunge(db, deposit)
    recid, record = deposit.fetch_published()

    # 'Simulate' a non-versioned record by removing 'conceptdoi' key
    del deposit['conceptdoi']
    del record['conceptdoi']
    deposit.commit()
    record.commit()
    db.session.commit()
    # Stash a copy of record metadata for later
    rec = deepcopy(record)

    record_uuid = str(record.id)

    assert dc_mock().metadata_delete.call_count == 0

    # users[0] is not an Admin but it doesn't matter in this case.
    delete_record(record.id, 'spam', users[0]['id'])

    # Make sure all PIDs are deleted
    # TODO: oai PID is left registered
    # assert PID.get('oai', rec['_oai']['id']) == PIDStatus.DELETED
    assert PID.get('doi', rec['doi']).status == PIDStatus.DELETED
    assert PID.get('recid', rec['recid']).status == PIDStatus.DELETED
    assert PID.get('recid', rec['conceptrecid']).status == PIDStatus.DELETED
    assert PID.get('depid', rec['_deposit']['id']).status == PIDStatus.DELETED

    assert dc_mock().metadata_delete.call_count == 1
    dc_mock().metadata_delete.assert_any_call('10.5072/zenodo.2')
    record = Record.get_record(record_uuid)
    assert record['removed_by'] == users[0]['id']
    assert record['removal_reason'] == 'Spam record, removed by Zenodo staff.'
