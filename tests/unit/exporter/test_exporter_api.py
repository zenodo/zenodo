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

"""Exporter stream tests."""

from __future__ import absolute_import, print_function

from invenio_files_rest.models import ObjectVersion
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from zenodo.modules.exporter.tasks import export_job


def test_exporter(app, db, es, exporter_bucket, record_with_files_creation):
    """Test record exporter."""
    pid, record, record_url = record_with_files_creation
    RecordIndexer().index_by_id(record.id)
    current_search.flush_and_refresh('records')

    with app.app_context():
        assert ObjectVersion.get_by_bucket(exporter_bucket).count() == 0
        export_job(job_id='records')
        assert ObjectVersion.get_by_bucket(exporter_bucket).count() == 1
