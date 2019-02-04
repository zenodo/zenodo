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

from celery import shared_task
from flask import current_app
from invenio_cache import current_cache
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.datacite import DataCiteProvider
from invenio_records import Record
from invenio_search.api import RecordsSearch
from lxml import etree

from zenodo.modules.records.models import AccessRight
from zenodo.modules.records.serializers import datacite_v41
from zenodo.modules.records.utils import find_registered_doi_pids, xsd41


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


@shared_task(ignore_result=True, rate_limit='1000/h')
def update_datacite_metadata(doi, object_uuid, job_id):
    """Update DataCite metadata of a single PersistentIdentifier.

    :param doi: Value of doi PID, with pid_type='doi'. It could be a normal
    DOI or a concept DOI.
    :type doi: str
    :param object_uuid: Record Metadata UUID.
    :type object_uuid: str
    :param job_id: id of the job to which this task belongs.
    :type job_id: str
    """
    task_details = current_cache.get('update_datacite:task_details')

    if task_details is None or job_id != task_details['job_id']:
        return

    record = Record.get_record(object_uuid)

    dcp = DataCiteProvider.get(doi)
    if dcp.pid.status != PIDStatus.REGISTERED:
        return

    doc = datacite_v41.serialize(dcp.pid, record)

    for validator in xsd41():
        validator.assertValid(etree.XML(doc.encode('utf8')))

    url = None
    if doi == record.get('doi'):
        url = current_app.config['ZENODO_RECORDS_UI_LINKS_FORMAT'].format(
            recid=str(record['recid']))
    elif doi == record.get('conceptdoi'):
        url = current_app.config['ZENODO_RECORDS_UI_LINKS_FORMAT'].format(
            recid=str(record['conceptrecid']))

    result = dcp.update(url, doc)
    if result is True:
        dcp.pid.updated = datetime.utcnow()
        db.session.commit()


@shared_task(ignore_result=True)
def schedule_update_datacite_metadata(max_count):
    """Schedule the update of DataCite metadata."""
    task_details = current_cache.get('update_datacite:task_details')

    if task_details is None or 'from_date' not in task_details or 'until_date' not in task_details:
        return

    doi_pids = find_registered_doi_pids(task_details['from_date'],
                                        task_details['until_date'],
                                        current_app.config['ZENODO_LOCAL_DOI_PREFIXES'])
    dois_count = doi_pids.count()

    task_details['left_pids'] = dois_count
    task_details['last_update'] = datetime.utcnow()
    current_cache.set('update_datacite:task_details', task_details, timeout=-1)

    if dois_count == 0:
        if 'finish_date' not in task_details:
            task_details['finish_date'] = datetime.utcnow()
            current_cache.set('update_datacite:task_details', task_details, timeout=-1)
        return

    scheduled_dois_count = max_count if max_count < dois_count else dois_count
    scheduled_dois_pids = doi_pids.limit(scheduled_dois_count)

    for doi_pid in scheduled_dois_pids:
        update_datacite_metadata.delay(doi_pid.pid_value,
                                       str(doi_pid.object_uuid),
                                       task_details['job_id'])
