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

import uuid

import pytest
from flask import url_for
from flask_principal import ActionNeed
from invenio_access.models import ActionUsers
from invenio_accounts.models import User
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import Record
from invenio_records_files.models import RecordsBuckets

from zenodo.modules.records.models import AccessRight


@pytest.mark.parametrize('user,access_right,expected', [
    (None, AccessRight.OPEN, 200),
    (None, AccessRight.EMBARGOED, 403),
    (None, AccessRight.CLOSED, 403),
    ('auth', AccessRight.OPEN, 200),
    ('auth', AccessRight.EMBARGOED, 403),
    ('auth', AccessRight.CLOSED, 403),
    ('owner', AccessRight.OPEN, 200),
    ('owner', AccessRight.EMBARGOED, 200),
    ('owner', AccessRight.CLOSED, 200),
    ('admin', AccessRight.OPEN, 200),
    ('admin', AccessRight.EMBARGOED, 200),
    ('admin', AccessRight.CLOSED, 200),
])
def test_file_permissions(app, db, test_object,  # fixtures
                          user, access_right, expected):
    """Test file permissions."""
    # Create test users
    admin = User(email='admin@zenodo.org', password='123456')
    owner = User(email='owner@zenodo.org', password='123456')
    auth = User(email='auth@zenodo.org', password='123456')
    db.session.add_all([admin, owner, auth])
    db.session.add(
        ActionUsers.allow(ActionNeed('admin-access'), user=admin)
    )

    # Create test record
    rec_uuid = uuid.uuid4()
    PersistentIdentifier.create(
        'recid',
        '1',
        object_type='rec',
        object_uuid=rec_uuid,
        status=PIDStatus.REGISTERED
    )
    Record.create({
        'recid': 1,
        'owners': [2],
        'access_right': access_right,
        '_files': [
            {
                'key': test_object.key,
                'bucket': str(test_object.bucket_id),
                'checksum': 'invalid'
            },
        ]
    }, id_=rec_uuid)
    db.session.add(
        RecordsBuckets(record_id=rec_uuid, bucket_id=test_object.bucket_id)
    )

    file_url = url_for(
        'invenio_records_ui.recid_files',
        pid_value='1',
        filename=test_object.key
    )

    db.session.commit()

    with app.test_client() as client:
        if user:
            # Login as user
            with client.session_transaction() as sess:
                sess['user_id'] = User.query.filter_by(
                    email='{}@zenodo.org'.format(user)).one().id
                sess['_fresh'] = True

        res = client.get(file_url)
        assert res.status_code == expected
