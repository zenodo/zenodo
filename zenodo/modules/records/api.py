# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

"""Record API."""

from __future__ import absolute_import

from flask import request
from os.path import splitext
from invenio_records_files.api import (FileObject, FilesIterator, Record,
                                       _writable)
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.models import PersistentIdentifier

from .fetchers import zenodo_record_fetcher


class ZenodoFileObject(FileObject):
    """Zenodo file object."""

    def dumps(self):
        """Create a dump."""
        super(ZenodoFileObject, self).dumps()
        self.data.update({
            # Remove dot from extension.
            'type': splitext(self.data['key'])[1][1:].lower(),
            'file_id': str(self.file_id),
        })
        return self.data


class ZenodoFilesIterator(FilesIterator):
    """Zenodo files iterator."""

    @_writable
    def __setitem__(self, key, stream):
        """Add file inside a deposit."""
        with db.session.begin_nested():
            size = None
            if request and request.files and request.files.get('file'):
                size = request.files['file'].content_length or None
            obj = ObjectVersion.create(
                bucket=self.bucket, key=key, stream=stream, size=size)
            self.filesmap[key] = self.file_cls(obj, {}).dumps()
            self.flush()


class ZenodoRecord(Record):
    """Zenodo Record."""

    file_cls = ZenodoFileObject

    files_iter_cls = ZenodoFilesIterator

    record_fetcher = staticmethod(zenodo_record_fetcher)

    @property
    def pid(self):
        """Return an instance of record PID."""
        pid = self.record_fetcher(self.id, self)
        return PersistentIdentifier.get(pid.pid_type, pid.pid_value)
