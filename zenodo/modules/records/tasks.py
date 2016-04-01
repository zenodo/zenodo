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

"""Celery background tasks."""

from __future__ import absolute_import, print_function

from celery import shared_task
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_records import Record

from zenodo.modules.records.models import AccessRight


@shared_task(ignore_result=True)
def update_expired_embargos():
    """Release expired embargoes every midnight."""
    record_ids = AccessRight.get_expired_embargos()
    for record in Record.get_records(record_ids):
        record['access_right'] = AccessRight.OPEN
        record.commit()
    db.session.commit()

    indexer = RecordIndexer()
    indexer.bulk_index(record_ids)
    indexer.process_bulk_queue()
