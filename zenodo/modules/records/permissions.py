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

from flask import current_app, request, session
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access import Permission
from invenio_files_rest.models import Bucket, MultipartObject, ObjectVersion
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_records_files.api import FileObject
from invenio_records_files.models import RecordsBuckets
from zenodo_accessrequests.models import SecretLink

from .api import ZenodoRecord
from .models import AccessRight
from .utils import is_deposit, is_record


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

    return Permission(ActionNeed('admin-access'))


def record_permission_factory(record=None, action=None):
    """Record permission factory."""
    return RecordPermission.create(record, action)


def record_create_permission_factory(record=None):
    """Create permission factory."""
    return record_permission_factory(record=record, action='create')


def record_read_permission_factory(record=None):
    """Read permission factory."""
    return record_permission_factory(record=record, action='read')


def record_read_files_permission_factory(record=None):
    """Read permission factory."""
    return record_permission_factory(record=record, action='read-files')


def record_update_permission_factory(record=None):
    """Update permission factory."""
    return record_permission_factory(record=record, action='update')


def record_delete_permission_factory(record=None):
    """Delete permission factory."""
    return record_permission_factory(record=record, action='delete')


def deposit_read_permission_factory(record=None):
    """Record permission factory."""
    if record and 'deposits' in record['$schema']:
        return DepositPermission.create(record=record, action='read')
    else:
        return RecordPermission.create(record=record, action='read')


def deposit_update_permission_factory(record=None):
    """Deposit update permission factory.

    Since Deposit API "actions" (eg. publish, discard, etc) are considered part
    of the "update" action, request context (if present) has to be used in
    order to figure out if this is an actual "update" or API action.
    """
    # TODO: The `need_record_permission` decorator of
    # `invenio_deposit.views.rest.DepositActionResource.post` should be
    # modified in order to be able to somehow provide a different permission
    # factory for the various Deposit API actions and avoid hacking our way
    # around to determine if it's an "action" or "update".
    if request and request.endpoint == 'invenio_deposit_rest.depid_actions':
        action = request.view_args.get('action')
        if action in DepositPermission.protected_actions:
            return DepositPermission.create(record=record, action=action)
    return DepositPermission.create(record=record, action='update')


def deposit_delete_permission_factory(record=None):
    """Record permission factory."""
    return DepositPermission.create(record=record, action='delete')


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
            return Permission(ActionNeed('admin-access')).can()


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
            return cls(record, has_read_files_permission)
        elif action in cls.admin_actions:
            return cls(record, has_admin_permission)
        else:
            return cls(record, deny)


class RecordPermission(object):
    """Record permission.

    - Create action given to any authenticated user.
    - Read access given to everyone.
    - Update access given to record owners.
    - Delete access given to admins only.
    """

    create_actions = ['create']
    read_actions = ['read']
    read_files_actions = ['read-files']
    update_actions = ['update']
    newversion_actions = ['newversion', 'registerconceptdoi']
    protected_actions = newversion_actions
    delete_actions = ['delete']

    def __init__(self, record, func, user):
        """Initialize a file permission object."""
        self.record = record
        self.func = func
        self.user = user or current_user

    def can(self):
        """Determine access."""
        return self.func(self.user, self.record)

    @classmethod
    def create(cls, record, action, user=None):
        """Create a record permission."""
        if action in cls.create_actions:
            return cls(record, allow, user)
        elif action in cls.read_actions:
            return cls(record, allow, user)
        elif action in cls.read_files_actions:
            return cls(record, has_read_files_permission, user)
        elif action in cls.update_actions:
            return cls(record, has_update_permission, user)
        elif action in (cls.newversion_actions):
            return cls(record, has_newversion_permission, user)
        elif action in cls.delete_actions:
            return cls(record, has_admin_permission, user)
        else:
            return cls(record, deny, user)


class DepositPermission(RecordPermission):
    """Deposit permission.

    - Read action given to record owners.
    - Delete action given to record owners (still subject to being unpublished)
    """

    @classmethod
    def create(cls, record, action, user=None):
        """Create a deposit permission."""
        if action in cls.read_actions:
            return cls(record, has_update_permission, user)
        elif action in cls.delete_actions:
            return cls(record, has_update_permission, user)
        return super(DepositPermission, cls).create(record, action, user=user)


#
# Utility functions
#
def deny(user, record):
    """Deny access."""
    return False


def allow(user, record):
    """Allow access."""
    return True


def has_read_files_permission(user, record):
    """Check if user has read access to the record."""
    # Allow if record is open access
    if AccessRight.get(
            record.get('access_right', 'closed'),
            record.get('embargo_date')) == AccessRight.OPEN:
        return True

    # Allow token bearers
    token = session.get('accessrequests-secret-token')
    if token and SecretLink.validate_token(
            token, dict(recid=int(record['recid']))):
        return True

    return has_update_permission(user, record)


def has_update_permission(user, record):
    """Check if user has update access to the record."""
    # Allow owners
    user_id = int(user.get_id()) if user.is_authenticated else None
    if user_id in record.get('owners', []):
        return True
    if user_id in record.get('_deposit', {}).get('owners', []):
        return True

    return has_admin_permission(user, record)


def has_newversion_permission(user, record):
    """Check if the user has permission to create a newversion for a record."""
    # Only the owner of the latest version can create new versions
    conceptrecid = record.get('conceptrecid')
    if conceptrecid:
        conceptrecid = PersistentIdentifier.get('recid', conceptrecid)
        pv = PIDVersioning(parent=conceptrecid)
        latest_recid = pv.last_child
        if latest_recid:
            latest_record = ZenodoRecord.get_record(pv.last_child.object_uuid)
            return has_update_permission(user, latest_record)
    return has_update_permission(user, record)


def has_admin_permission(user, record):
    """Check if user has admin access to record."""
    # Allow administrators
    if Permission(ActionNeed('admin-access')):
        return True
