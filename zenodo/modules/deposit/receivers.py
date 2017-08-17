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

"""Zenodo Deposit module receivers."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_sipstore.models import RecordSIP

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.openaire.tasks import openaire_direct_index
from zenodo.modules.sipstore.tasks import archive_sip


def datacite_register_after_publish(sender, action=None, pid=None,
                                    deposit=None):
    """Mind DOI with DataCite after the deposit has been published."""
    if action == 'publish' and \
            current_app.config['DEPOSIT_DATACITE_MINTING_ENABLED']:
        recid_pid, record = deposit.fetch_published()
        datacite_register.delay(recid_pid.pid_value, str(record.id))


def openaire_direct_index_after_publish(sender, action=None, pid=None,
                                        deposit=None):
    """Send published record for direct indexing at OpenAIRE."""
    if current_app.config['OPENAIRE_DIRECT_INDEXING_ENABLED']:
        _, record = deposit.fetch_published()
        if action in 'publish':
            openaire_direct_index.delay(record_uuid=str(record.id))


def sipstore_write_files_after_publish(sender, action=None, pid=None,
                                       deposit=None):
    """Send the SIP for archiving."""
    if action == 'publish' and \
            current_app.config['SIPSTORE_ARCHIVER_WRITING_ENABLED']:
        recid_pid, record = deposit.fetch_published()
        sip = (
            RecordSIP.query
            .filter_by(pid_id=recid_pid.id)
            .order_by(RecordSIP.created.desc())
            .first().sip
        )
        archive_sip.delay(str(sip.id))
