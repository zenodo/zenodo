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

from __future__ import absolute_import, print_function

import pytest
from flask import url_for
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers
from invenio_accounts.models import User

from zenodo.modules.records.models import AccessRight


@pytest.mark.parametrize('user,access_right,expected', [
    (None, AccessRight.OPEN, 200),
    (None, AccessRight.EMBARGOED, 404),
    (None, AccessRight.CLOSED, 404),
    ('auth', AccessRight.OPEN, 200),
    ('auth', AccessRight.EMBARGOED, 404),
    ('auth', AccessRight.CLOSED, 404),
    ('owner', AccessRight.OPEN, 200),
    ('owner', AccessRight.EMBARGOED, 200),
    ('owner', AccessRight.CLOSED, 200),
    ('admin', AccessRight.OPEN, 200),
    ('admin', AccessRight.EMBARGOED, 200),
    ('admin', AccessRight.CLOSED, 200),
])
def test_file_permissions(app, db, record_with_files_creation,
                          user, access_right, expected):
    """Test file permissions."""
    pid, record, record_url = record_with_files_creation

    # Create test users
    admin = User(email='admin@zenodo.org', password='123456')
    owner = User(email='owner@zenodo.org', password='123456')
    auth = User(email='auth@zenodo.org', password='123456')
    db.session.add_all([admin, owner, auth])
    db.session.add(
        ActionUsers.allow(ActionNeed('admin-access'), user=admin)
    )
    db.session.commit()

    # Create test record
    record['access_right'] = access_right
    record['owners'] = [owner.id]
    record.commit()
    db.session.commit()

    file_url = url_for(
        'invenio_records_ui.recid_files',
        pid_value=pid.pid_value,
        filename='Test.pdf',
    )
    with app.test_client() as client:
        if user:
            # Login as user
            with client.session_transaction() as sess:
                sess['user_id'] = User.query.filter_by(
                    email='{}@zenodo.org'.format(user)).one().id
                sess['_fresh'] = True

        res = client.get(file_url)
        assert res.status_code == expected
