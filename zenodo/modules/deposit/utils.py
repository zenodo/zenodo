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

import uuid

from flask import abort, request
from werkzeug.local import LocalProxy
from werkzeug.routing import PathConverter


def file_id_to_key(value):
    """Convert file UUID to value if in request context."""
    from invenio_files_rest.models import ObjectVersion

    _, record = request.view_args['pid_value'].data
    if value in record.files:
        return value

    try:
        value = uuid.UUID(value)
    except ValueError:
        abort(404)

    object_version = ObjectVersion.query.filter_by(
        bucket_id=record.files.bucket.id, file_id=value
    ).first()
    if object_version:
        return object_version.key
    return value


class FileKeyConverter(PathConverter):
    """Convert file UUID for key."""

    def to_python(self, value):
        """Lazily convert value from UUID to key if need be."""
        return LocalProxy(lambda: file_id_to_key(value))


def get_all_deposit_siblings(deposit):
    from invenio_pidstore.models import PersistentIdentifier
    from invenio_pidrelations.contrib.versioning import PIDVersioning
    recid = deposit['recid']
    rec_pid = PersistentIdentifier.get(pid_type='recid', pid_value=str(recid))
    pv = PIDVersioning(child=rec_pid)
    return [pid.get_assigned_object() for pid in pv.children]
