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

"""Zenodo Auditor tasks."""

from __future__ import absolute_import

import uuid

from celery import shared_task
from flask import current_app
from invenio_communities.models import Community

from .oai import OAIAudit
from .records import RecordAudit
from .utils import all_records, get_file_logger


@shared_task(ignore_results=True)
def audit_records(logfile=None):
    """Audit all records.

    :param str logfile: Logfile path for encountered issues.
    """
    logger = current_app.logger
    audit_id = audit_records.request.id or uuid.uuid4()
    if logfile:
        logger = get_file_logger(logfile, 'records', audit_id)
    audit = RecordAudit(audit_id, logger, all_records())
    for check in audit:
        pass


@shared_task(ignore_results=True)
def audit_oai(logfile=None):
    """Audit OAI sets.

    :param str logfile: Logfile path for encountered issues.
    """
    logger = current_app.logger
    audit_id = audit_oai.request.id or uuid.uuid4()
    if logfile:
        logger = get_file_logger(logfile, 'oai', audit_id)
    audit = OAIAudit(audit_id, logger, Community.query.all())
    try:
        for check in audit:
            pass
    except Exception:
        raise
    finally:
        audit.clear_db_oai_set_cache()
