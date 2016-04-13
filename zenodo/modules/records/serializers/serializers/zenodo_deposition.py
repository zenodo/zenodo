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

"""Marshmallow based JSON serializer with translation for records."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.json import JSONSerializer

from zenodo.modules.records.serializers.schemas.legacy import \
    LegacyDepositionSchemaV1

import copy

import pytz


class ZenodoDepositionSerializer(JSONSerializer):
    """Marshmallow based JSON serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, translator, replace_refs=False):
        """Initialize record."""
        self.translator = translator
        super(JSONSerializer, self).__init__(
                LegacyDepositionSchemaV1, replace_refs)

    def preprocess_record(self, pid, record, links_factory=None):
        """Prepare a record and persistent identifier for serialization."""
        record = copy.deepcopy(record.replace_refs()) if self.replace_refs \
            else record.dumps()

        result = self.translator(record)
        result['created'] = (pytz.utc.localize(record.created).isoformat()
                             if record.created else None)
        result['doi_url'] = None
        result['id'] = record['_deposit']['id']
        result['modified'] = (pytz.utc.localize(record.updated).isoformat()
                              if record.updated else None)
        result['record_url'] = None
        result['state'] = record['_deposit']['status']
        result['submitted'] = result['state'] == 'done'
        return result
