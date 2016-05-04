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

"""Access controls for files on Zenodo."""

from __future__ import absolute_import, print_function

from flask_login import current_user
from flask_principal import ActionNeed
from invenio_access import DynamicPermission
from invenio_records_files.models import RecordsBuckets

from zenodo.modules.records.models import AccessRight


class FilePermission(object):
    """Permission factory for files on Zenodo."""

    def __init__(self, bucket, action='objects-read'):
        """Initialize a file permission object."""
        self.bucket = bucket
        self.action = action

    def can(self):
        """Check if the current user has permission to access file."""
        rb = RecordsBuckets.query.filter_by(bucket_id=self.bucket.id).one()

        # Open records are available to everyone
        if rb.record.json['access_right'] == AccessRight.OPEN:
            return True

        # Users can access their own files
        if current_user.is_authenticated and \
                int(current_user.get_id()) in rb.record.json.get('owners', []):
            return True

        # Admins can access every file
        if DynamicPermission(ActionNeed('admin-access')).can():
            return True

        return False
