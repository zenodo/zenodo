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

from flask import current_app, session
from flask_babelex import gettext as _
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access import DynamicPermission
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_records.api import Record
from invenio_records_files.api import FileObject
from invenio_records_files.models import RecordsBuckets
from invenio_search import current_search
from invenio_search.utils import schema_to_index
from zenodo_accessrequests.models import SecretLink

from zenodo.modules.records.models import AccessRight


def files_permission_factory(obj, action=None):
    """Permission for files are always based on the type of bucket.

    1. Community bucket: Read access for everyone
    2. Record bucket: Read access only with open and restricted access.
    3. Deposit bucket: Read/update with restricted access.
    4. Any other bucket is restricted to admins only.
    """
    # Extract bucket id
    bucket_id = None
    if isinstance(obj, Bucket):
        bucket_id = str(obj.id)
    elif isinstance(obj, ObjectVersion):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, MultipartObject):
        bucket_id = str(obj.bucket_id)
    elif isinstance(obj, FileObject):
        bucket_id = str(obj.bucket_id)

    # Retrieve record
    if bucket_id is not None:
        # Community bucket
        if str(bucket_id) == current_app.config['COMMUNITIES_BUCKET_UUID']:
            return CommunityBucketPermission(action)

        # Record or deposit bucket
        rb = RecordsBuckets.query.filter_by(bucket_id=bucket_id).one_or_none()
        if rb is not None:
            record = Record.get_record(rb.record_id)
            if is_record(record):
                return RecordFilesPermission.create(record, action)
            elif is_deposit(record):
                return DepositFilesPermission.create(record, action)

    return DynamicPermission(ActionNeed('admin-access'))


#
# Helper methods
#
def schema_prefix(schema):
    """Get index prefix for a given schema."""
    if not schema:
        return None
    index, doctype = schema_to_index(
        schema, index_names=current_search.mappings.keys())
    return index.split('-')[0]


def is_record(record):
    """Determine if a record is a bibliographic record."""
    return schema_prefix(record.get('$schema')) == 'records'


def is_deposit(record):
    """Determine if a record is a deposit record."""
    return schema_prefix(record.get('$schema')) == 'deposits'


#
# Permission classes
#
class CommunityBucketPermission(object):
    """Permission for files in community bucket.

    Everyone are allowed to read. Admin can do everything.
    """

    def __init__(self, action):
        """Initialize permission."""
        self.action = action

    def can(self):
        """Check permission."""
        if self.action == 'object-read':
            return True
        else:
            return DynamicPermission(ActionNeed('admin-access')).can()


class DepositFilesPermission(object):
    """Permission for files in deposit records (read and update access).

    Read and update access given to owners and administrators.
    """

    update_actions = [
        'bucket-read',
        'bucket-read-versions',
        'bucket-update',
        'bucket-listmultiparts',
        'object-read',
        'object-read-version',
        'object-delete',
        'object-delete-version',
        'multipart-read',
        'multipart-delete',
    ]

    def __init__(self, record, func):
        """Initialize a file permission object."""
        self.record = record
        self.func = func

    def can(self):
        """Determine access."""
        return self.func(current_user, self.record)

    @classmethod
    def create(cls, record, action):
        """Record and instance."""
        if action in cls.update_actions:
            return cls(record, has_update_permission)
        else:
            return cls(record, has_admin_permission)


class RecordFilesPermission(DepositFilesPermission):
    """Permission for files in published records (read only access).

    Read access (list and download) granted to:

      1. Everyone if record is open access.
      2. Owners, token bearers and administrators if embargoed, restricted or
         closed access

    Read version access granted to:

      1. Administrators only.
    """

    read_actions = [
        'bucket-read',
        'object-read',
    ]

    admin_actions = [
        'bucket-read',
        'bucket-read-versions',
        'object-read',
        'object-read-version',
    ]

    @classmethod
    def create(cls, record, action):
        """Create a record files permission."""
        if action in cls.read_actions:
            return cls(record, has_read_permission)
        elif action in cls.admin_actions:
            return cls(record, has_admin_permission)
        else:
            return cls(record, deny)


#
# Utility functions
#
def deny(user, record):
    """Deny access."""
    return False


def has_read_permission(user, record):
    """Check if user has read access to the record."""
    # Allow if record is open access
    reason = 'You have access because {0}'

    if AccessRight.get(record['access_right'], record.get('embargo_date')) \
            == AccessRight.OPEN:
        return _(reason.format('the record has open access'))

    # Allow token bearers
    token = session.get('accessrequests-secret-token')
    if token and SecretLink.validate_token(
            token, dict(recid=int(record['recid']))):
        return True

    return has_update_permission(user, record)


def has_update_permission(user, record):
    """Check if user has update access to the record."""
    reason = 'You have access because {0}'
    # Allow owners
    user_id = int(user.get_id()) if user.is_authenticated else None
    if user_id in record.get('owners', []):
        return _(reason.format('you are the owner'))

    if has_admin_permission(user, record):
        return _(reason.format('you have administrator access'))


def has_admin_permission(user, record):
    """Check if user has admin access to record."""
    # Allow administrators
    if DynamicPermission(ActionNeed('admin-access')):
        return True
