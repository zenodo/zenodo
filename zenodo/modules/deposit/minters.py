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

"""Persistent identifier minters."""

from __future__ import absolute_import

from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier


def zenodo_concept_recid_minter(record_uuid=None, data=None):
    """Mint the Concept RECID.

    Reserves the Concept RECID for the record.
    """
    parent_id = RecordIdentifier.next()
    conceptrecid = PersistentIdentifier.create(
        pid_type='recid',
        pid_value=str(parent_id),
        status=PIDStatus.RESERVED,
    )
    data['conceptrecid'] = conceptrecid.pid_value
    return conceptrecid


def zenodo_deposit_minter(record_uuid, data):
    """Mint the DEPID, and reserve the Concept RECID and RECID PIDs."""
    if 'conceptrecid' not in data:
        zenodo_concept_recid_minter(data=data)

    recid = zenodo_reserved_record_minter(data=data)

    # Create depid with same pid_value of the recid
    depid = PersistentIdentifier.create(
        'depid',
        str(recid.pid_value),
        object_type='rec',
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED,
    )

    data.update({
        '_deposit': {
            'id': depid.pid_value,
            'status': 'draft',
        },
    })

    return depid


def zenodo_reserved_record_minter(record_uuid=None, data=None):
    """Reserve a recid."""
    id_ = RecordIdentifier.next()
    recid = PersistentIdentifier.create(
        'recid', str(id_), status=PIDStatus.RESERVED
    )
    data['recid'] = int(recid.pid_value)

    return recid
