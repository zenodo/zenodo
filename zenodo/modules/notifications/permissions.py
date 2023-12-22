# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2023 CERN.
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

"""Permissions for users using the notifications module."""

from __future__ import absolute_import

from invenio_access import Permission, action_factory
from zenodo.modules.tokens import decode_rat


class SendNotificationPermission(object):
    """Permission for sending notifications from trusted parties.
    """

    create_actions = ['notifications-send-notification']

    def __init__(self, record, func, user=None):
        """Initialize a file permission object."""
        self.record = record
        self.func = func
        self.user = user or current_user

    def can(self):
        """Determine access."""
        return self.func(self.user)

    @classmethod
    def create(cls, record, action):
        """Record and instance."""
        token = request.args.get('token')
        if token and action in cls.create_actions:
            rat_signer, payload = decode_rat(rat_token)
            rat_access = payload.get('access')
            if rat_access == 'create':
                rat_deposit_id = payload.get('deposit_id')
                deposit_id = record.get('_deposit', {}).get('id')
                if rat_deposit_id == deposit_id:
                    return cls(record, has_update_permission, user=rat_signer)
        if action in cls.update_actions:
            return cls(record, has_update_permission)
        else:
            return cls(record, has_admin_permission)

