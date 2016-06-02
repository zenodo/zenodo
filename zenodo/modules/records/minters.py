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

import idutils
from flask import current_app
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider


def zenodo_record_minter(record_uuid, data):
    """Mint record identifier (and DOI)."""
    if 'recid' in data:
        recid = PersistentIdentifier.get('recid', data['recid'])
        recid.assign('rec', record_uuid)
        recid.register()
    else:
        recid = RecordIdProvider.create(
            object_type='rec', object_uuid=record_uuid).pid
        data['recid'] = int(recid.pid_value)

    zenodo_doi_minter(record_uuid, data)

    return recid


def zenodo_doi_minter(record_uuid, data):
    """Mint DOI."""
    doi = data.get('doi')
    status = PIDStatus.RESERVED
    provider = None
    prefix = current_app.config['PIDSTORE_DATACITE_DOI_PREFIX']

    # Create a DOI if no DOI was found.
    if not doi:
        assert 'recid' in data
        doi = '{prefix}/zenodo.{recid}'.format(
            prefix=prefix,
            recid=data['recid'],
        )
        data['doi'] = doi

    assert idutils.is_doi(doi)

    if doi.startswith('{0}/'.format(prefix)):
        provider = 'datacite'

    return PersistentIdentifier.create(
        'doi',
        doi,
        pid_provider=provider,
        object_type='rec',
        object_uuid=record_uuid,
        status=status,
    )
