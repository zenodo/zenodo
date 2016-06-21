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

"""Utilities for Zenodo deposit."""

from flask import has_request_context
from flask_security import current_user
from invenio_deposit.permissions import admin_permission_factory


class DepositPermission(object):
    """Zenodo deposit edit permission."""

    def __init__(self, record, *args, **kwargs):
        """Initialize a deposit permission object."""
        self.record = record

    def can(self):
        """Check if the current user has permission to access file.

        This method must align with the search class filtering of records.
        """
        if not has_request_context() or admin_permission_factory().can():
            return True
        else:
            uid = getattr(current_user, 'id', 0)
            if uid in self.record.get('_deposit', {}).get('owners', []):
                return True
        return False


def can_edit_deposit(record):
    """Check edit deposit permissions."""
    return DepositPermission(record).can()
