# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016, 2017, 2018 CERN.
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

"""Marshmallow based DataCite serializer for records."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_records_rest.serializers.datacite import DataCite31Serializer, \
    DataCite41Serializer

from .pidrelations import preprocess_related_identifiers
from .schemas.common import ui_link_for


class ZenodoDataCite31Serializer(DataCite31Serializer):
    """Marshmallow based DataCite serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def preprocess_record(self, pid, record, links_factory=None):
        """Add related identifiers from PID relations."""
        result = super(ZenodoDataCite31Serializer, self).preprocess_record(
            pid, record, links_factory=links_factory
        )
        # Versioning links
        result = preprocess_related_identifiers(pid, record, result)
        # Alternate identifiers
        altidentifiers = result['metadata'].get('alternate_identifiers', [])
        altidentifiers.append({
            'identifier': ui_link_for('record_html', id=str(record['recid'])),
            'scheme': 'url',
        })
        result['metadata']['alternate_identifiers'] = altidentifiers
        return result


class ZenodoDataCite41Serializer(DataCite41Serializer):
    """Marshmallow based DataCite serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def preprocess_record(self, pid, record, links_factory=None):
        """Add related identifiers from PID relations."""
        result = super(ZenodoDataCite41Serializer, self).preprocess_record(
            pid, record, links_factory=links_factory
        )
        # Versioning links
        result = preprocess_related_identifiers(pid, record, result)
        # Alternate identifiers
        altidentifiers = result['metadata'].get('alternate_identifiers', [])
        altidentifiers.append({
            'identifier': ui_link_for('record_html', id=str(record['recid'])),
            'scheme': 'url'
        })
        result['metadata']['alternate_identifiers'] = altidentifiers
        return result
