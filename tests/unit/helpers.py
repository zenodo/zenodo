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

"""Helpers."""

from copy import deepcopy

from flask import current_app

from zenodo.modules.deposit.api import ZenodoDeposit as Deposit


def bearer_auth(headers, token):
    """Create authentication headers (with a valid oauth2 token)."""
    headers = deepcopy(headers)
    headers.append(
        ('Authorization', 'Bearer {0}'.format(token['token'].access_token))
    )
    return headers


def login_user_via_session(client, user=None, email=None):
    """Login a user via the session."""
    if not user:
        user = current_app.extensions['security'].datastore.find_user(
            email=email)
    with client.session_transaction() as sess:
        sess['user_id'] = user.get_id()


def publish_and_expunge(db, deposit):
    """Publish the deposit and expunge the session.

    Use this if you want to be safe that session is synced with the DB after
    the deposit publishing.
    """
    deposit.publish()
    dep_uuid = deposit.id
    db.session.commit()
    db.session.expunge_all()
    deposit = Deposit.get_record(dep_uuid)
    return deposit
