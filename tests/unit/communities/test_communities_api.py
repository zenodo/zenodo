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

"""Test Zenodo communities API."""

from __future__ import absolute_import, print_function

from helpers import publish_and_expunge
from invenio_communities.models import InclusionRequest
from invenio_pidrelations.contrib.versioning import PIDVersioning
from six import BytesIO, b

from zenodo.modules.communities.api import ZenodoCommunity
from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.records.resolvers import record_resolver


def test_basic_api(app, db, communities, deposit, deposit_file):
    """Test basic workflow using Deposit and Communities API."""
    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']

    recid_v1, record_v1 = deposit_v1.fetch_published()
    recid_v1_value = recid_v1.pid_value

    deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.object_uuid)
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    deposit_v2 = deposit_v2.edit()
    # 1. Request for 'c1' and 'c2' through deposit v2
    deposit_v2['communities'] = ['c1', 'c2', ]
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()
    recid_v2_value = recid_v2.pid_value
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    assert record_v1.get('communities', []) == []
    assert record_v2.get('communities', []) == []

    c1_api = ZenodoCommunity('c1')
    c2_api = ZenodoCommunity('c2')

    # Inclusion requests should be visible for both records
    assert c1_api.get_comm_irs(record_v1, pid=recid_v1).count() == 1
    assert c1_api.get_comm_irs(record_v2, pid=recid_v2).count() == 1

    assert c2_api.get_comm_irs(record_v1, pid=recid_v1).count() == 1
    assert c2_api.get_comm_irs(record_v2, pid=recid_v2).count() == 1

    # Accept to 'c1' through record_v2 (as originally requested),
    # and 'c2' through record_v1 (version)
    c1_api.accept_record(record_v2, pid=recid_v2)
    c2_api.accept_record(record_v1, pid=recid_v1)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    recid_v2, record_v2 = record_resolver.resolve(recid_v2_value)
    # Accepting individual record to a community should propagate the changes
    # to all versions
    assert record_v1['communities'] == record_v2['communities'] == \
        ['c1', 'c2', ]

    # Removing 'c1' from deposit_v1 should remove it from two published records
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    deposit_v1 = deposit_v1.edit()
    deposit_v1['communities'] = []
    deposit_v1 = publish_and_expunge(db, deposit_v1)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    recid_v2, record_v2 = record_resolver.resolve(recid_v2_value)
    assert record_v1.get('communities', []) == []
    assert record_v2.get('communities', []) == []


def test_autoadd(mocker, app, db, users, communities, deposit, deposit_file,
                 communities_autoadd_enabled, communities_mail_enabled):
    """Test basic workflow using Deposit and Communities API."""
    email_mock = mocker.patch(
        'invenio_communities.receivers.send_community_request_email')
    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']

    recid_v1, record_v1 = deposit_v1.fetch_published()
    recid_v1_value = recid_v1.pid_value

    deposit_v1 = deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    depid_v2_value = depid_v2.pid_value
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    deposit_v2 = deposit_v2.edit()
    # 1. Request for 'c1' and 'c3' (owned by user) through deposit v2
    deposit_v2['communities'] = ['c1', 'c2', 'c3', ]
    deposit_v2['grants'] = [{'title': 'SomeGrant'}, ]
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()
    assert record_v2['grants'] == [{'title': 'SomeGrant'}, ]
    recid_v2_value = recid_v2.pid_value
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    assert record_v1.get('communities', []) == ['c3', 'grants_comm']
    assert record_v2.get('communities', []) == ['c3', 'grants_comm']
    assert deposit_v1.get('communities', []) == ['c1', 'c2', 'c3', 'ecfunded',
                                                 'grants_comm', 'zenodo']
    assert deposit_v2.get('communities', []) == ['c1', 'c2', 'c3', 'ecfunded',
                                                 'grants_comm', 'zenodo']
    # 'c3' and 'grants_comm' were automatically added (no mail sent),
    # while 'c1', 'c2', and 'ecfunded' and 'zenodo' are requested for,
    # however, for 'c2' and 'zenodo', notifications have been disabled
    assert email_mock.call_count == 2

    c1_api = ZenodoCommunity('c1')
    c2_api = ZenodoCommunity('c2')
    c3_api = ZenodoCommunity('c3')
    grants_comm_api = ZenodoCommunity('grants_comm')
    ecfunded_api = ZenodoCommunity('ecfunded')
    zenodo_api = ZenodoCommunity('zenodo')

    # Inclusion requests should be visible for both records
    assert c1_api.get_comm_irs(record_v1, pid=recid_v1).count() == 1
    assert c1_api.get_comm_irs(record_v2, pid=recid_v2).count() == 1
    assert c2_api.get_comm_irs(record_v1, pid=recid_v1).count() == 1
    assert c2_api.get_comm_irs(record_v2, pid=recid_v2).count() == 1
    assert c3_api.get_comm_irs(record_v1, pid=recid_v1).count() == 0
    assert c3_api.get_comm_irs(record_v2, pid=recid_v2).count() == 0
    assert grants_comm_api.get_comm_irs(
        record_v1, pid=recid_v1).count() == 0
    assert grants_comm_api.get_comm_irs(
        record_v2, pid=recid_v2).count() == 0
    assert ecfunded_api.get_comm_irs(
        record_v1, pid=recid_v1).count() == 1
    assert ecfunded_api.get_comm_irs(
        record_v2, pid=recid_v2).count() == 1
    assert zenodo_api.get_comm_irs(record_v1, pid=recid_v1).count() == 1
    assert zenodo_api.get_comm_irs(record_v2, pid=recid_v2).count() == 1

    # Accept to 'c1' through record_v2 (as originally requested),
    # and 'c2' through record_v1 (resolved through version)
    c1_api.accept_record(record_v2, pid=recid_v2)
    c2_api.accept_record(record_v1, pid=recid_v1)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    recid_v2, record_v2 = record_resolver.resolve(recid_v2_value)
    # Accepting individual record to a community should propagate the changes
    # to all versions
    assert record_v1.get('communities', []) == ['c1', 'c2', 'c3',
                                                'grants_comm']
    assert record_v2.get('communities', []) == ['c1', 'c2', 'c3',
                                                'grants_comm']
    assert deposit_v1.get('communities', []) == ['c1', 'c2', 'c3', 'ecfunded',
                                                 'grants_comm', 'zenodo']
    assert deposit_v2.get('communities', []) == ['c1', 'c2', 'c3', 'ecfunded',
                                                 'grants_comm', 'zenodo']

    # Removing 'c1'-'c3' from deposit_v1 should remove it from two published
    # records and other deposits as well
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    deposit_v1 = deposit_v1.edit()
    deposit_v1['communities'] = []
    deposit_v1 = publish_and_expunge(db, deposit_v1)
    depid_v2, deposit_v2 = deposit_resolver.resolve(depid_v2_value)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    recid_v2, record_v2 = record_resolver.resolve(recid_v2_value)
    assert record_v1.get('communities', []) == ['grants_comm', ]
    assert record_v2.get('communities', []) == ['grants_comm', ]
    assert deposit_v1.get('communities', []) == ['ecfunded', 'grants_comm',
                                                 'zenodo']
    assert deposit_v2.get('communities', []) == ['ecfunded', 'grants_comm',
                                                 'zenodo']


def test_autoadd_explicit(
        app, db, users, communities, deposit, deposit_file,
        communities_autoadd_enabled):
    """Explicitly the autoadded communities."""
    deposit['communities'] = ['ecfunded', 'grants_comm', 'zenodo']
    deposit['grants'] = [{'title': 'SomeGrant'}, ]
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit_v1.fetch_published()

    assert record_v1.get('communities', []) == ['grants_comm', ]
    assert deposit_v1.get('communities', []) == ['ecfunded', 'grants_comm',
                                                 'zenodo']


def test_autoadd_explicit_newversion(
        app, db, users, communities, deposit, deposit_file,
        communities_autoadd_enabled):
    """Explicitly the autoadded communities in a new version."""
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    depid_v1_value = deposit_v1['_deposit']['id']
    recid_v1_value = recid_v1.pid_value

    deposit_v1 = deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    depid_v2_value = depid_v2.pid_value

    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())

    deposit_v2['communities'] = ['ecfunded', 'grants_comm', 'zenodo']
    deposit_v2['grants'] = [{'title': 'SomeGrant'}, ]
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    depid_v2, deposit_v2 = deposit_resolver.resolve(depid_v2_value)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    assert record_v1.get('communities', []) == ['grants_comm', ]
    assert deposit_v1.get('communities', []) == ['ecfunded', 'grants_comm',
                                                 'zenodo']
    assert record_v2.get('communities', []) == ['grants_comm', ]
    assert deposit_v2.get('communities', []) == ['ecfunded', 'grants_comm',
                                                 'zenodo']


def test_communities_newversion_addition(
        app, db, users, communities, deposit, deposit_file):
    """Make sure that new version of record synchronizes the communities."""
    deposit['communities'] = ['c1', 'c2']
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    depid_v1_value = deposit_v1['_deposit']['id']
    recid_v1_value = recid_v1.pid_value

    c1_api = ZenodoCommunity('c1')
    c2_api = ZenodoCommunity('c2')

    c1_api.accept_record(record_v1, pid=recid_v1)
    c2_api.accept_record(record_v1, pid=recid_v1)

    deposit_v1 = deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    depid_v2_value = depid_v2.pid_value

    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())

    # Remove 'c2' and request for 'c5'. Make sure that communities from
    # previous record version are preserved/removed properly
    deposit_v2['communities'] = ['c1', 'c5']
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    depid_v2, deposit_v2 = deposit_resolver.resolve(depid_v2_value)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    assert record_v1.get('communities', []) == ['c1', ]
    assert deposit_v1.get('communities', []) == ['c1', 'c5', ]
    assert record_v2.get('communities', []) == ['c1', ]
    assert deposit_v2.get('communities', []) == ['c1', 'c5', ]


def test_communities_newversion_while_ir_pending_bug(
        app, db, users, communities, deposit, deposit_file):
    """Make sure that pending IRs remain after a new version (bug)."""
    deposit['communities'] = ['c1', 'c2']
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    depid_v1_value = deposit_v1['_deposit']['id']
    recid_v1_value = recid_v1.pid_value

    # Two inclusion requests are pending
    assert InclusionRequest.query.count() == 2

    # Accept one community
    c1_api = ZenodoCommunity('c1')
    c1_api.accept_record(record_v1, pid=recid_v1)

    deposit_v1 = deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    depid_v2_value = depid_v2.pid_value

    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())

    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    depid_v2, deposit_v2 = deposit_resolver.resolve(depid_v2_value)
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    # Make sure there is still IR to community 'c2' after newversion
    assert InclusionRequest.query.count() == 1
    assert InclusionRequest.query.one().id_community == 'c2'
    assert record_v1.get('communities', []) == ['c1', ]
    assert deposit_v1.get('communities', []) == ['c1', 'c2', ]
    assert record_v2.get('communities', []) == ['c1', ]
    assert deposit_v2.get('communities', []) == ['c1', 'c2', ]


def test_propagation_with_newversion_open(
        app, db, users, communities, deposit, deposit_file):
    """Adding old versions to a community should propagate to all drafts."""
    # deposit['communities'] = ['c1', 'c2']
    deposit_v1 = publish_and_expunge(db, deposit)
    deposit_v1 = deposit_v1.edit()

    recid_v1, record_v1 = deposit_v1.fetch_published()
    recid_v1_value = recid_v1.pid_value

    deposit_v1 = deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    depid_v2_value = depid_v2.pid_value

    # New version in 'deposit_v2' has not been published yet
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())

    # depid_v1_value = deposit_v1['_deposit']['id']
    # depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    deposit_v1['communities'] = ['c1', 'c2', ]
    deposit_v1 = publish_and_expunge(db, deposit_v1)

    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    c1_api = ZenodoCommunity('c1')
    c1_api.accept_record(record_v1, pid=recid_v1)

    depid_v2, deposit_v2 = deposit_resolver.resolve(depid_v2_value)
    assert deposit_v2['communities'] == ['c1', 'c2']
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()

    assert record_v2['communities'] == ['c1', ]
