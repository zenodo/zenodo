# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Celery tasks for Zenodo Deposit."""

from __future__ import absolute_import

from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PIDStatus, PersistentIdentifier
from invenio_pidstore.providers.datacite import DataCiteProvider
from invenio_records_files.api import Record

from zenodo.modules.records.minters import is_local_doi
from zenodo.modules.records.serializers import datacite_v31
from zenodo.modules.records.serializers.pidrelations import \
    serialize_related_identifiers


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def datacite_register(pid_value, record_uuid):
    """Mint DOI and Concept DOI with DataCite.

    :param pid_value: Value of record PID, with pid_type='recid'.
    :type pid_value: str
    :param record_uuid: Record Metadata UUID.
    :type record_uuid: str
    """
    try:
        record = Record.get_record(record_uuid)
        # Bail out if not a Zenodo DOI.
        if not is_local_doi(record['doi']):
            return

        dcp = DataCiteProvider.get(record['doi'])
        doc = datacite_v31.serialize(dcp.pid, record)

        url = current_app.config['ZENODO_RECORDS_UI_LINKS_FORMAT'].format(
            recid=pid_value)
        if dcp.pid.status == PIDStatus.REGISTERED:
            dcp.update(url, doc)
        else:
            dcp.register(url, doc)

        # If this is the latest record version, update/register the Concept DOI
        # using the metadata of the record.
        recid = PersistentIdentifier.get('recid', str(record['recid']))
        pv = PIDVersioning(child=recid)
        if pv.exists and pv.is_last_child:
            conceptdoi = record.get('conceptdoi')
            conceptrecid = record.get('conceptrecid')
            concept_dcp = DataCiteProvider.get(conceptdoi)
            url = current_app.config['ZENODO_RECORDS_UI_LINKS_FORMAT'].format(
                recid=conceptrecid)

            # Update related identifiers
            record_rel_ids = record.pop('related_identifiers', [])
            parent_rel_ids = serialize_related_identifiers(pv.parent)
            for version_ri in parent_rel_ids:
                if version_ri not in record_rel_ids:
                    record_rel_ids.append(version_ri)
            record['related_identifiers'] = record_rel_ids

            doc = datacite_v31.serialize(dcp.pid, record)
            if concept_dcp.pid.status == PIDStatus.REGISTERED:
                concept_dcp.update(url, doc)
            else:
                concept_dcp.register(url, doc)

        db.session.commit()
    except Exception as exc:
        datacite_register.retry(exc=exc)


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def datacite_inactivate(pid_value):
    """Mint the DOI with DataCite.

    :param pid_value: Value of record PID, with pid_type='recid'.
    :type pid_value: str
    """
    try:
        dcp = DataCiteProvider.get(pid_value)
        dcp.delete()
        db.session.commit()
    except Exception as exc:
        datacite_inactivate.retry(exc=exc)
