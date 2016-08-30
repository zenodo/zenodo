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

from flask import url_for
from invenio_accounts.testutils import login_user_via_session


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
