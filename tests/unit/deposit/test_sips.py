# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo deposit workflow."""

from __future__ import absolute_import, print_function

import json

from flask_security import login_user
from invenio_sipstore.models import SIP, RecordSIP, SIPFile, SIPMetadata
from six import BytesIO


def test_basic_workflow(app, db, users, deposit):
    """Test simple deposit publishing workflow."""
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        datastore = app.extensions['security'].datastore
        login_user(datastore.get_user(users[0]['email']))
        deposit.files['one.txt'] = BytesIO(b'Test')
        deposit.files['two.txt'] = BytesIO(b'Test2')
        deposit = deposit.publish()
        # Should create one SIP, one RecordSIP and two SIPFiles
        assert SIP.query.count() == 1
        assert SIPMetadata.query.count() == 1
        assert RecordSIP.query.count() == 1
        assert SIPFile.query.count() == 2
        sip = SIP.query.one()
        assert sip.user_id == users[0]['id']
        assert sip.agent['email'] == users[0]['email']
        assert sip.agent['ip_address'] == '127.0.0.1'
        assert len(sip.sip_files) == 2
        assert sip.sip_files[0].sip_id == sip.id
        assert sip.sip_files[1].sip_id == sip.id

        # Publishing the second time shuld create a new SIP and new RecordSIP
        # but no new SIPFiles. This is under assumption that users cannot
        # upload new files to the already published deposit.
        deposit = deposit.edit()
        deposit['title'] = 'New Title'
        deposit = deposit.publish()

        assert SIP.query.count() == 2
        assert RecordSIP.query.count() == 2
        assert SIPMetadata.query.count() == 2
        assert SIPFile.query.count() == 2

        # Fetch the last RecordSIP and make sure, that
        # the corresponding SIP doesn't have any files
        recsip = RecordSIP.query.order_by(RecordSIP.created.desc()).first()
        assert not recsip.sip.sip_files


def test_programmatic_publish(app, db, deposit, deposit_file):
    """Test publishing by without request.

    Might never happen, but at least shouldn't crash the system.
    """
    deposit = deposit.publish()
    pid, record = deposit.fetch_published()
    sip = SIP.query.one()
    assert not sip.user_id
    assert sip.sip_metadata[0].content == json.dumps(record.dumps())
    assert sip.sip_metadata[0].type.format == 'json'
    assert sip.sip_metadata[0].type.name == 'test-json'
    assert sip.sip_metadata[0].type.schema == \
        'https://zenodo.org/schemas/records/record-v1.0.0.json'
    assert len(sip.record_sips) == 1
    assert sip.record_sips[0].pid_id == pid.id
    assert len(sip.agent) == 1  # Just the '$schema' key in agent info
    assert sip.agent['$schema'] == \
        'https://zenodo.org/schemas/sipstore/agent-webclient-v1.0.0.json'


def test_anonymous_request(app, db, deposit):
    """Test sip creation during an anonymous request."""
    with app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        deposit.files['one.txt'] = BytesIO(b'Test')
        deposit.files['two.txt'] = BytesIO(b'Test2')
        deposit.publish()
        sip = SIP.query.one()
        assert sip.user_id is None
        assert 'email' not in sip.agent
        assert sip.agent['ip_address'] == '127.0.0.1'
        assert len(sip.sip_files) == 2
        assert sip.sip_files[0].sip_id == sip.id
        assert sip.sip_files[1].sip_id == sip.id
