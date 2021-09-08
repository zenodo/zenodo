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

"""Zenodo communities fixture loading."""

from __future__ import absolute_import, print_function

from datetime import date, datetime, time, timedelta

from flask import current_app
from flask_security.utils import hash_password
from invenio_access.models import ActionUsers
from invenio_accounts.models import User
from invenio_db import db


def loaduser(user_data):
    """Load a single user to Zenodo from JSON fixture."""
    kwargs = {
        'email': user_data['email'],
        'password': hash_password(user_data['password']),
        'active': user_data.get('active', True),
        'confirmed_at': datetime.utcnow() - timedelta(days=30),
    }

    datastore = current_app.extensions['security'].datastore
    datastore.create_user(**kwargs)
    db.session.commit()
    user = User.query.filter_by(email=user_data['email']).one()
    actions = current_app.extensions['invenio-access'].actions
    actionusers_f = {
        'allow': ActionUsers.allow,
        'deny': ActionUsers.deny,
    }
    # e.g. [('allow', 'admin-access'), ]
    for action_type, action_name in user_data.get('access', []):
        action = actions[action_name]
        db.session.add(
            actionusers_f[action_type](action, user_id=user.id)
        )
    db.session.commit()
