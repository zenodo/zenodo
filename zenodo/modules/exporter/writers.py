# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Data model package."""

from __future__ import absolute_import, print_function

from datetime import datetime

from invenio_db import db
from invenio_files_rest.models import ObjectVersion


class BucketWriter(object):
    """Export writer that writes to an object in a bucket."""

    def __init__(self, bucket_id=None, key=None, **kwargs):
        """Initialize writer."""
        self.bucket_id = bucket_id
        self.key = key
        self.obj = None

    def open(self):
        """Open the bucket for writing."""
        self.obj = ObjectVersion.create(
            self.bucket_id,
            self.key() if callable(self.key) else self.key
        )
        db.session.commit()
        return self

    def write(self, stream):
        """Write the data stream to the object."""
        self.obj.set_contents(stream)

    def close(self,):
        """Close bucket file."""
        db.session.commit()


def filename_factory(**kwargs):
    """Get a function which generates a filename with a timestamp."""
    return lambda: '{name}-{timestamp}.{format}'.format(
        timestamp=datetime.utcnow().replace(microsecond=0).isoformat(),
        **kwargs
    )
