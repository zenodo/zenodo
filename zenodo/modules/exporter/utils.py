# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utils for exporter."""

from __future__ import absolute_import, print_function

from uuid import UUID

from flask import current_app
from invenio_db import db
from invenio_files_rest.errors import FilesException
from invenio_files_rest.models import Bucket, Location


def initialize_exporter_bucket():
    """Initialize the bucket for exporter module metadata dumps.

    :raises: `invenio_files_rest.errors.FilesException`
    """
    bucket_id = UUID(current_app.config['EXPORTER_BUCKET_UUID'])

    if Bucket.query.get(bucket_id):
        raise FilesException("Bucket with UUID {} already exists.".format(
            bucket_id))
    else:
        storage_class = current_app.config['FILES_REST_DEFAULT_STORAGE_CLASS']
        location = Location.get_default()
        bucket = Bucket(id=bucket_id,
                        location=location,
                        default_storage_class=storage_class)
        db.session.add(bucket)
        db.session.commit()
