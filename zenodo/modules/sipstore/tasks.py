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

"""Celery tasks for SIPStore."""

from __future__ import absolute_import

from celery import shared_task
from invenio_db import db
from invenio_sipstore.api import SIP as SIPApi
from invenio_sipstore.archivers import BagItArchiver
from invenio_sipstore.models import SIP


@shared_task(ignore_result=True, rate_limit='100/m')
def archive_sip(sip_uuid):
    """Send the SIP for archiving.

    :param sip_uuid: UUID of the SIP for archiving.
    :type sip_uuid: str
    """
    sip = SIPApi(SIP.query.get(sip_uuid))
    archiver = BagItArchiver(sip)
    bagmeta = archiver.get_bagit_metadata(sip)
    if bagmeta is None:
        raise Exception('Bagit metadata does not exist for SIP: {0}.'.format(
            sip.id))
    if sip.archived:
        raise Exception('SIP was already archived {0}.'.format(
            sip.id))
    archiver.write_all_files()
    sip.archived = True
    db.session.commit()
