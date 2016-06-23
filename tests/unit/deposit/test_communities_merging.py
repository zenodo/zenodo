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

from invenio_communities.models import Community, InclusionRequest

from zenodo.modules.deposit.api import ZenodoDeposit as Deposit


def _publish_and_expunge(db, deposit):
    """Publish the deposit and expunge the session.

    Use this if you want to be safe that session is synced with the DB after
    the deposit publishing."""
    deposit.publish()
    dep_uuid = deposit.id
    db.session.commit()
    db.session.expunge_all()
    deposit = Deposit.get_record(dep_uuid)
    return deposit


def test_basic_community_workflow(app, db, communities, deposit, deposit_file):
    """Test simple (without concurrent events) deposit publishing workflow."""
    deposit = _publish_and_expunge(db, deposit)
    assert InclusionRequest.query.count() == 0
    pid, record = deposit.fetch_published()
    assert not record.get('communities', [])

    # Open record for edit, request a community and publish
    deposit = deposit.edit()
    deposit['communities'] = ['c1', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()

    # Should contain just an InclusionRequest
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c1'
    assert ir.id_record == record.id

    # Accept a record to the community 'c1'
    c1 = Community.get('c1')
    c1.accept_record(record)
    record.commit()
    db.session.commit()
    assert InclusionRequest.query.count() == 0
    assert record['communities'] == ['c1', ]

    # Open for edit and request another community
    deposit = deposit.edit()
    assert deposit['communities'] == ['c1', ]
    deposit['communities'] = ['c1', 'c2', ]  # New request for community 'c2'
    deposit = _publish_and_expunge(db, deposit)
    deposit['communities'] = ['c1', 'c2', ]
    pid, record = deposit.fetch_published()
    assert record['communities'] == ['c1', ]
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c2'
    assert ir.id_record == record.id

    # Reject the request for community 'c2'
    c2 = Community.get('c2')
    c2.reject_record(record)
    db.session.commit()
    deposit = deposit.edit()

    # The deposit should not contain obsolete inclusion requests
    assert deposit['communities'] == ['c1', ]
    assert InclusionRequest.query.count() == 0
    pid, record = deposit.fetch_published()
    assert record['communities'] == ['c1', ]

    # Request for removal from a previously accepted community 'c1'
    deposit['communities'] = []
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert not deposit.get('communities', [])
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 0


def test_accept_while_edit(app, db, communities, deposit, deposit_file):
    """Test deposit publishing with concurrent events.

    Accept a record, while deposit in open edit and then published.
    """
    deposit['communities'] = ['c1', 'c2']
    deposit = _publish_and_expunge(db, deposit)
    assert InclusionRequest.query.count() == 2
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c2']
    assert not record.get('communities', [])

    # Open for edit
    deposit = deposit.edit()
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c2']
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 2

    # Accept a record meanwhile
    c1 = Community.get('c1')
    c1.accept_record(record)
    record.commit()
    db.session.commit()

    # Publish and make sure nothing is missing
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c2']
    assert record['communities'] == ['c1', ]
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c2'
    assert ir.id_record == record.id


def test_reject_while_edit(app, db, communities, deposit, deposit_file):
    """Test deposit publishing with concurrent events.

    Reject a record, while deposit in open edit and published.
    """
    # Request for community 'c1'
    deposit['communities'] = ['c1', ]
    deposit = _publish_and_expunge(db, deposit)
    assert deposit['communities'] == ['c1', ]
    pid, record = deposit.fetch_published()
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c1'
    assert ir.id_record == record.id

    # Open deposit in edit mode and request another community 'c2'
    deposit = deposit.edit()
    deposit['communities'] = ['c1', 'c2']

    # Reject the request for community 'c1'
    c1 = Community.get('c1')
    c1.reject_record(record)
    db.session.commit()

    # Publish the deposit
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    # NOTE: 'c1' is requested again!
    assert InclusionRequest.query.count() == 2
    ir1 = InclusionRequest.query.filter_by(id_community='c1').one()
    ir2 = InclusionRequest.query.filter_by(id_community='c2').one()
    assert ir1.id_record == record.id
    assert ir2.id_record == record.id
    assert deposit['communities'] == ['c1', 'c2']
    assert not record.get('communities', [])


def test_record_modified_while_edit(app, db, communities, deposit,
                                    deposit_file):
    """Test deposit publishing with concurrent events.

    Modify a record, while deposit in open edit and then published.
    """
    deposit['communities'] = ['c1', ]
    deposit = _publish_and_expunge(db, deposit)
    assert InclusionRequest.query.count() == 1
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', ]
    assert not record.get('communities', [])

    # Open for edit
    deposit = deposit.edit()
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', ]
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 1

    # Meanwhile, a record is modified
    record['title'] = 'Other title'
    record.commit()
    db.session.commit()

    # Publish and make sure nothing is missing
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', ]
    assert not record.get('communities', [])
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c1'
    assert ir.id_record == record.id


def test_remove_obsolete_irs(app, db, communities, deposit, deposit_file):
    """Test removal of obsolete IRs in-between deposit edits."""
    # Request for 'c1'
    deposit['communities'] = ['c1', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert InclusionRequest.query.count() == 1
    assert deposit['communities'] == ['c1', ]
    assert not record.get('communities', [])

    # Open for edit and remove the request to community 'c1'
    deposit = deposit.edit()
    deposit['communities'] = []
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert InclusionRequest.query.count() == 0
    assert not deposit.get('communities', [])
    assert not record.get('communities', [])


def test_remove_community_by_key_del(app, db, communities, deposit,
                                     deposit_file):
    """Test removal of communities by key deletion.

    Communities can be removed by not providing or deleting the communities
    from the key depsit. Moremover, the redundant 'empty' keys should not be
    automatically added to deposit nor record."""
    # If 'communities' key was not in deposit metadata,
    # it shouldn't be automatically added
    assert 'communities' not in deposit
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert 'communities' not in deposit
    assert 'communities' not in record

    # Request for 'c1' and 'c2'
    deposit = deposit.edit()
    deposit['communities'] = ['c1', 'c2', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    # No reason to have 'communities' in record since nothing was accepted
    assert 'communities' not in record

    # Accept 'c1'
    c1 = Community.get('c1')
    c1.accept_record(record)
    record.commit()

    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c2', ]
    assert InclusionRequest.query.count() == 1
    assert record['communities'] == ['c1', ]

    # Remove the key from deposit and publish
    deposit = deposit.edit()
    del deposit['communities']
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert 'communities' not in deposit
    assert 'communities' not in record
    assert InclusionRequest.query.count() == 0


def test_autoaccept_owned_communities(app, db, users, communities, deposit,
                                      deposit_file):
    """Automatically accept records requested by community owners."""
    # 'c3' is owned by the user, but not 'c1'
    deposit['communities'] = ['c1', 'c3', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c3', ]
    assert record['communities'] == ['c3', ]
    assert InclusionRequest.query.count() == 1
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'c1'
    assert ir.id_record == record.id

    # Edit the deposit, and add more communities
    # 'c4' should be added automatically, but not 'c2'
    deposit = deposit.edit()
    deposit['communities'] = ['c1', 'c2', 'c3', 'c4', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['c1', 'c2', 'c3', 'c4', ]
    assert record['communities'] == ['c3', 'c4', ]
    assert InclusionRequest.query.count() == 2
    ir1 = InclusionRequest.query.filter_by(id_community='c1').one()
    ir2 = InclusionRequest.query.filter_by(id_community='c2').one()
    assert ir1.id_record == record.id
    assert ir2.id_record == record.id


def test_fixed_communities(app, db, users, communities, deposit, deposit_file):
    """Test automatic adding and requesting to fixed communities."""

    app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'] = ['zenodo', ]
    app.config['ZENODO_COMMUNITIES_ADD_IF_GRANTS'] = ['ecfunded', ]

    deposit['grants'] = [{'title': 'SomeGrant'}, ]
    # 'c3' is owned by one of the deposit owner
    assert Community.get('c3').id_user in deposit['_deposit']['owners']
    deposit['communities'] = ['c3', ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert record['communities'] == ['c3', 'ecfunded']
    assert deposit['communities'] == ['c3', 'ecfunded', 'zenodo']
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'zenodo'
    assert ir.id_record == record.id

    # FIXME: Since app is yielded, those two variables have to be unset.
    app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'] = list()
    app.config['ZENODO_COMMUNITIES_ADD_IF_GRANTS'] = list()


def test_fixed_communities_after_edit(app, db, users, communities, deposit,
                                      deposit_file):
    """Test automatic adding and requesting to fixed communities.

    Add to ecfunded also after later addition of grant information.
    """

    app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'] = ['zenodo', ]
    app.config['ZENODO_COMMUNITIES_ADD_IF_GRANTS'] = ['ecfunded', ]

    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['zenodo', ]
    assert 'communities' not in record
    ir = InclusionRequest.query.one()
    assert ir.id_community == 'zenodo'
    assert ir.id_record == record.id

    deposit = deposit.edit()
    deposit['grants'] = [{'title': 'SomeGrant'}, ]
    deposit = _publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert deposit['communities'] == ['ecfunded', 'zenodo', ]
    assert record['communities'] == ['ecfunded', ]

    app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'] = list()
    app.config['ZENODO_COMMUNITIES_ADD_IF_GRANTS'] = list()
