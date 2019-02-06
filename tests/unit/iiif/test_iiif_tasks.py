# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo thumbnails tests."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_cache import current_cache
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search
from pkg_resources import resource_stream
from werkzeug import LocalProxy

from zenodo.modules.iiif.tasks import preprocess_thumbnails


def test_preprocess_thumbnails(app, db, es, record_with_bucket, iiif_cache):
    pid, record = record_with_bucket
    filename = 'test.png'
    record.files[filename] = resource_stream(
        'zenodo.modules.theme',
        'static/img/screenshots/github.png'
        )
    record.files[filename]['type'] = 'png'
    record.commit()
    db.session.commit()
    RecordIndexer().index(record)
    current_search.flush_and_refresh(index='records')
    preprocess_thumbnails('zenodo')
    key = 'iiif:'+str(record.files['test.png'].obj)+'/full/250,/default/0.png'
    assert iiif_cache.get(key)
    iiif_cache.delete(key)
    preprocess_thumbnails('zenodo')
    assert not iiif_cache.get(key)
