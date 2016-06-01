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

"""Persistent identifier minters."""

from __future__ import absolute_import

from invenio_pidstore.models import PersistentIdentifier, PIDStatus, \
    RecordIdentifier


def zenodo_deposit_minter(record_uuid, data):
    """Mint deposit identifier."""
    id_ = RecordIdentifier.next()
    depid = PersistentIdentifier.create(
        'depid',
        str(id_),
        object_type='rec',
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED,
    )
    # Reserve recid with same number.
    PersistentIdentifier.create(
        'recid', depid.pid_value,
        status=PIDStatus.RESERVED
    )
    data.update({
        '_deposit': {
            'id': depid.pid_value,
            'status': 'draft',
        },
        'recid': id_,
    })
    return depid
