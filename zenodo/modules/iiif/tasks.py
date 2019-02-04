# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017, 2018 CERN.
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

"""Celery background tasks."""

from __future__ import absolute_import, print_function

from datetime import datetime

import arrow
from celery import shared_task
from flask import current_app
from flask_iiif.restful import IIIFImageAPI
from invenio_cache import current_cache
from invenio_iiif.utils import iiif_image_key
from invenio_indexer.api import RecordIndexer
from invenio_search.api import RecordsSearch


@shared_task(ignore_result=True)
def preprocess_thumbnails(community):
    """Schedule the preprocessing of arcadia type of records thumbnails."""
    last_preprocessing_time = current_cache.get('last_preprocessing_time')\
        or arrow.get(datetime.min).to('utc')
    current_preprocessing_time = arrow.utcnow()

    search = RecordsSearch(index='records')
    q = (search.query({
        "range": {"created": {
            "gte": str(last_preprocessing_time),
            "lt":  str(current_preprocessing_time)
        }}}
    ).filter({
        "term": {
            "communities": community
        }}
    ).source(include=['_files']))
    records_files = q.scan()
    for record_files in records_files:
        for object_file in record_files.to_dict().get('_files', []):
            if(object_file['type'] not in ['jpg', 'png', 'tif', 'tiff']):
                continue
            size = '250,'
            thumbnail = IIIFImageAPI().get(
                version='v2',
                uuid=str(iiif_image_key(object_file)),
                region='full',
                size=size,
                rotation='0',
                quality='default',
                image_format=str(object_file['type']))
    current_cache.set('last_preprocessing_time',
                      str(current_preprocessing_time), timeout=-1)
