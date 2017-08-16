# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Utilities for SIPStore module."""

import json

from invenio_sipstore.archivers.utils import chunks
from invenio_sipstore.models import SIPMetadata, SIPMetadataType


def generate_bag_path(recid, revision):
    """Generates a path for the BagIt.

    Splits the recid string into chunks of size 3, e.g.:
    recid='12345', revision='5' -> ['123', '45', 'r', '5']

    :param recid: recid value
    :type recid: str
    :param revision: revision of the record
    :type revision: str
    """
    recid_chunks = list(chunks(recid, 3))
    return recid_chunks + ['r', revision, ]


def archive_directory_builder(sip):
    """Generate a path for BagIt from SIP.

    :param sip: SIP which is to be archived
    :type SIP: invenio_sipstore.models.SIP
    :return: list of str
    """
    jsonmeta = SIPMetadata.query.get(
        (sip.id, SIPMetadataType.get_from_name('json').id))
    if jsonmeta is not None:
        data = json.loads(jsonmeta.content)
        revision = str(data['_deposit']['pid']['revision_id'])
    else:
        revision = "0"
    recid = sip.model.record_sips[0].pid.pid_value
    return generate_bag_path(recid, revision)


def sipmetadata_name_formatter(sipmetadata):
    """Generator for the archived SIPMetadata filenames."""
    return "record-{name}.{format}".format(
        name=sipmetadata.type.name,
        format=sipmetadata.type.format
    )
