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

import arrow
from invenio_sipstore.archivers.utils import chunks


def generate_bag_path(recid, iso_timestamp):
    """Generates a path for the BagIt.

    Splits the recid string into chunks of size 3, e.g.:
    generate_bag_path('12345', '2017-09-15T11:44:24.590537+00:00') ==
        ['123', '45', 'r', '2017-09-15T11:44:24.590537+00:00']

    :param recid: recid value
    :type recid: str
    :param iso_timestamp: ISO-8601 formatted creation date (UTC) of the SIP.
    :type iso_timestamp: str
    """
    recid_chunks = list(chunks(recid, 3))
    return recid_chunks + ['r', iso_timestamp, ]


def archive_directory_builder(sip):
    """Generate a path for BagIt from SIP.

    :param sip: SIP which is to be archived
    :type SIP: invenio_sipstore.models.SIP
    :return: list of str
    """
    iso_timestamp = arrow.get(sip.model.created).isoformat()
    recid = sip.model.record_sips[0].pid.pid_value
    return generate_bag_path(recid, iso_timestamp)


def sipmetadata_name_formatter(sipmetadata):
    """Generator for the archived SIPMetadata filenames."""
    return "record-{name}.{format}".format(
        name=sipmetadata.type.name,
        format=sipmetadata.type.format
    )
