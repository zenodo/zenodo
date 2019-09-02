# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

"""Extra formats utilities."""

from flask import current_app
from invenio_files_rest.models import Bucket
from invenio_records_files.models import RecordsBuckets
from werkzeug.local import LocalProxy


class ExtraFormats(object):
    """Extra formats utilities."""

    mimetype_whitelist = LocalProxy(
        lambda: current_app.config.get(
            'ZENODO_EXTRA_FORMATS_MIMETYPE_WHITELIST', {})
    )
    """MIMEType whitelist."""

    @classmethod
    def get_or_create_bucket(cls, record):
        """Get or create the extra formats bucket for a record (or deposit)."""
        if not record.get('_buckets', {}).get('extra_formats'):
            extra_formats_bucket = Bucket.create(
                quota_size=current_app.config[
                    'ZENODO_EXTRA_FORMATS_BUCKET_QUOTA_SIZE'],
                max_file_size=current_app.config['ZENODO_MAX_FILE_SIZE'],
                locked=False
            )
            cls.link_to_record(record, extra_formats_bucket)
        else:
            extra_formats_bucket = Bucket.query.get(
                record['_buckets']['extra_formats'])
        return extra_formats_bucket

    @classmethod
    def link_to_record(cls, record, bucket):
        """Link a record its extra formats bucket."""
        if not record.get('_buckets', {}).get('extra_formats'):
            record.setdefault('_buckets', {})
            record['_buckets']['extra_formats'] = str(bucket.id)
            record.commit()
            RecordsBuckets.create(record=record.model, bucket=bucket)
