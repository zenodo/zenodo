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

from flask import session
from flask_login import current_user
from flask_principal import ActionNeed
from invenio_access import DynamicPermission
from invenio_records_files.models import RecordsBuckets
from zenodo_accessrequests.models import SecretLink

from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from zenodo.modules.records.models import AccessRight


class RESTFilePermissionFactory(object):
    """Invenio-Files-Rest permission factory."""

    def __init__(self, bucket, action='objects-read'):
        """Initialize a file permission object."""
        self.bucket = bucket
        self.action = action

    def can(self):
        """Check if the current user has permission to access file."""
        if isinstance(self.bucket, Bucket):
            bucket_id = str(self.bucket.id)
        elif isinstance(self.bucket, ObjectVersion):
            bucket_id = str(self.bucket.bucket_id)
        elif isinstance(self.bucket, MultipartObject):
            bucket_id = str(self.bucket.bucket_id)
        else:
            raise RuntimeError('Unknown object')

        rb = RecordsBuckets.query.filter_by(
            bucket_id=bucket_id).one_or_none()
        if rb is not None:
            return has_access(current_user, rb.record.json)
        return True


def has_access(user=None, record=None):
    """Check whether the user has access to the record.

    The rules followed are:
        1. Open Access records can be viewed by everyone.
        2. Embargoed, Restricted and Closed records can be viewed by
           the record owners.
        3. Administrators can view every record.
    """
    if AccessRight.get(record['access_right'], record.get('embargo_date')) \
            == AccessRight.OPEN:
        return True

    user_id = int(user.get_id()) if user.is_authenticated else None

    if user_id in record.get('owners', []):
        return True

    if DynamicPermission(ActionNeed('admin-access')):
        return True

    try:
        token = session['accessrequests-secret-token']
        recid = record['recid']
        if SecretLink.validate_token(token, dict(recid=int(recid))):
            return True
        else:
            del session['accessrequests-secret-token']
    except KeyError:
        pass

    return False
