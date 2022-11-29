# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Celery tasks for OpenAIRE."""

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

import requests
from celery import shared_task
from flask import current_app
from invenio_cache import current_cache
from invenio_pidstore.models import PersistentIdentifier

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.serializers import openaire_json_v1

from .errors import OpenAIRERequestError
from .helpers import is_openaire_dataset, is_openaire_other, \
    is_openaire_publication, is_openaire_software, openaire_datasource_id, \
    openaire_original_id, openaire_type


def _openaire_request_factory(headers=None, auth=None):
    """Request factory for OpenAIRE API."""
    ses = requests.Session()
    ses.headers.update(headers or {'Content-type': 'application/json',
                                   'Accept': 'application/json'})
    if not auth:
        username = current_app.config.get('OPENAIRE_API_USERNAME')
        password = current_app.config.get('OPENAIRE_API_PASSWORD')
        if username and password:
            auth = (username, password)
    ses.auth = auth
    return ses


@shared_task(ignore_result=True, max_retries=6,
             default_retry_delay=4 * 60 * 60, rate_limit='100/m')
def openaire_direct_index(record_uuid, retry=True):
    """Send record for direct indexing at OpenAIRE.

    :param record_uuid: Record Metadata UUID.
    :type record_uuid: str
    """
    try:
        record = ZenodoRecord.get_record(record_uuid)

        # Bail out if not an OpenAIRE record.
        if not (is_openaire_publication(record) or
                is_openaire_dataset(record) or
                is_openaire_software(record) or
                is_openaire_other(record)):
            return

        data = openaire_json_v1.serialize(record.pid, record)
        url = '{}/feedObject'.format(
            current_app.config['OPENAIRE_API_URL'])
        req = _openaire_request_factory()
        res = req.post(url, data=data, timeout=10)

        if not res.ok:
            raise OpenAIRERequestError(res.text)

        res_beta = None
        if current_app.config['OPENAIRE_API_URL_BETA']:
            url_beta = '{}/feedObject'.format(
                current_app.config['OPENAIRE_API_URL_BETA'])
            res_beta = req.post(url_beta, data=data, timeout=10)

        if res_beta and not res_beta.ok:
            raise OpenAIRERequestError(res_beta.text)
        else:
            recid = record.get('recid')
            current_cache.delete('openaire_direct_index:{}'.format(recid))
    except Exception as exc:
        recid = record.get('recid')
        current_cache.set('openaire_direct_index:{}'.format(recid),
                          datetime.now(), timeout=-1)
        if retry:
            openaire_direct_index.retry(exc=exc)
        else:
            raise exc


@shared_task(ignore_result=True, max_retries=6,
             default_retry_delay=4 * 60 * 60, rate_limit='100/m')
def openaire_delete(record_uuid=None, original_id=None, datasource_id=None):
    """Delete record from OpenAIRE index.

    :param record_uuid: Record Metadata UUID.
    :type record_uuid: str
    :param original_id: OpenAIRE originalId.
    :type original_id: str
    :param datasource_id: OpenAIRE datasource identifier.
    :type datasource_id: str
    """
    try:
        record = ZenodoRecord.get_record(record_uuid, with_deleted=True)
        if record and 'resource_type' not in record:
            # record was deleted, find last revision with metadata
            record = next(
                r for r in reversed(record.revisions)
                if 'resource_type' in r
            )
        if not record:
            raise OpenAIRERequestError('Could not resolve record.')
        # Resolve originalId and datasource if not already available
        if not (original_id and datasource_id):
            original_id = openaire_original_id(
                record, openaire_type(record))[1]
            datasource_id = openaire_datasource_id(record)

        params = {'originalId': original_id, 'collectedFromId': datasource_id}
        req = _openaire_request_factory()
        res = req.delete(current_app.config['OPENAIRE_API_URL'], params=params)
        res_beta = None
        if current_app.config['OPENAIRE_API_URL_BETA']:
            res_beta = req.delete(
                current_app.config['OPENAIRE_API_URL_BETA'], params=params)

        if not res.ok or (res_beta and not res_beta.ok):
            raise OpenAIRERequestError(res.text)

        # Remove from failures cache
        current_cache.delete(
            'openaire_direct_index:{}'.format(record['recid']))

    except Exception as exc:
        current_cache.set(
            'openaire_direct_index:{}'.format(record['recid']),
            datetime.now(), timeout=-1)
        openaire_delete.retry(exc=exc)


@shared_task
def retry_openaire_failures():
    """Retries failed OpenAIRE indexing/deletion operations."""
    cache = current_cache.cache
    redis_client = cache._read_clients
    failed_recids = redis_client.scan_iter(
        match=(cache.key_prefix + 'openaire_direct_index:*'),
        count=1000,
    )
    for key in failed_recids:
        recid_value = key.split('openaire_direct_index:')[1]
        recid = PersistentIdentifier.query.filter_by(
            pid_type='recid', pid_value=recid_value).one_or_none()
        record = ZenodoRecord.get_record(recid.object_uuid, with_deleted=True)
        if 'resource_type' in record:
            openaire_direct_index.delay(str(record.id), retry=False)
        else:
            openaire_delete.delay(str(record.id))
