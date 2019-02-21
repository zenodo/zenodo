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

from os.path import splitext

from flask import current_app, request
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import FileObject, FilesIterator, Record, \
    _writable

from .fetchers import zenodo_record_fetcher
from collections import OrderedDict


class MetaFilesException(Exception):
    """Metafiles exception."""


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

    def __init__(self, *args, **kwargs):
        """Initialize files iterator."""
        super(ZenodoFilesIterator, self).__init__(*args, **kwargs)
        # TODO: This should solve all of our problems?
        self.filesmap = OrderedDict([
            (f['key'], f) for f in self.record.get('_files', [])
            if not f['key'].startswith(self.metafiles_prefix)
        ])

    @property
    def metafiles_prefix(self):
        """Metafiles key prefix."""
        return current_app.config['ZENODO_METAFILE_KEY_PREFIX']

    @_writable
    def __setitem__(self, key, stream):
        """Add file inside a deposit."""
        if key.startswith(self.metafiles_prefix):
            raise MetaFilesException(
                'You cannot add a file with the "{}" prefix.'
                .format(self.metafiles_prefix))
        with db.session.begin_nested():
            size = None
            if request and request.files and request.files.get('file'):
                size = request.files['file'].content_length or None
            obj = ObjectVersion.create(
                bucket=self.bucket, key=key, stream=stream, size=size)
            self.filesmap[key] = self.file_cls(obj, {}).dumps()
            self.flush()


class MetaFilesMixin(object):
    """Meafiles mixin."""

    @property
    def metafiles(self):
        """Metafiles iterator."""
        return MetaFilesIterator(
            self, bucket=self.files.bucket, file_cls=self.file_cls)


class MetaFilesIterator(ZenodoFilesIterator):
    """Metafiles mixin."""

    def __init__(self, *args, **kwargs):
        """Initialize metafiles with a record."""
        super(MetaFilesIterator, self).__init__(*args, **kwargs)
        self.filesmap = OrderedDict([
            (f['key'], f) for f in self.record.get('_files', [])
            if f['key'].startswith(self.metafiles_prefix)
        ])

    @property
    def mimetype_whitelist(self):
        """Whitelisted mimetypes for metafiles."""
        return current_app.config['ZENODO_DERIVED_METADATA_MIMETYPE_WHITELIST']

    def metafile_key(self, mimetype):
        """Get metafile key for a specific mimetype."""
        return '{}{}'.format(self.metafiles_prefix, mimetype)

    # NOTE: No "_writable" decorator used here
    def __setitem__(self, key, stream):
        """Add file inside a deposit."""
        key = self.metafile_key(key)
        with db.session.begin_nested():
            size = None
            if request and request.files and request.files.get('file'):
                size = request.files['file'].content_length or None
            obj = ObjectVersion.create(
                bucket=self.bucket, key=key, stream=stream, size=size)
            self.filesmap[key] = self.file_cls(obj, {}).dumps()
            self.flush()


class ZenodoRecord(Record, MetaFilesMixin):
    """Zenodo Record."""

    file_cls = ZenodoFileObject

    files_iter_cls = ZenodoFilesIterator

    record_fetcher = staticmethod(zenodo_record_fetcher)

    @property
    def pid(self):
        """Return an instance of record PID."""
        pid = self.record_fetcher(self.id, self)
        return PersistentIdentifier.get(pid.pid_type, pid.pid_value)

    @property
    def depid(self):
        """Return depid of the record."""
        return PersistentIdentifier.get(
            pid_type='depid',
            pid_value=self.get('_deposit', {}).get('id')
        )
