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

"""Exporter programmatic API."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.fetchers import zenodo_record_fetcher
from zenodo.modules.records.serializers import json_v1

from .streams import BZip2ResultStream
from .writers import BucketWriter, filename_factory

EXPORTER_BUCKET_UUID = '00000000-0000-0000-0000-000000000001'

EXPORTER_JOBS = {
    'records': {
        'index': 'records',
        'serializer': json_v1,
        'writer': BucketWriter(
            bucket_id=EXPORTER_BUCKET_UUID,
            key=filename_factory(index='records', format='json.bz2'),
        ),
        'resultstream_cls': BZip2ResultStream,
        'pid_fetcher': zenodo_record_fetcher,
    }
}
"""Export jobs definitions."""
