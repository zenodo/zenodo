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

"""Zenodo Serializers."""

from __future__ import absolute_import, print_function

from flask import has_request_context
from flask_security import current_user
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_records_files.api import Record
from invenio_records_rest.serializers.json import JSONSerializer

from zenodo.modules.records.serializers.pidrelations import \
    serialize_related_identifiers

from ..permissions import has_read_files_permission


class ZenodoJSONSerializer(JSONSerializer):
    """Zenodo JSON serializer.

    Adds or removes files from depending on access rights and provides a
    context to the request serializer.
    """

    def preprocess_record(self, pid, record, links_factory=None):
        """Include files for single record retrievals."""
        result = super(ZenodoJSONSerializer, self).preprocess_record(
            pid, record, links_factory=links_factory
        )
        # Add/remove files depending on access right.
        if isinstance(record, Record) and '_files' in record:
            if not has_request_context() or has_read_files_permission(
                    current_user, record):
                result['files'] = record['_files']

        # Serialize PID versioning as related identifiers
        pv = PIDVersioning(child=pid)
        if pv.exists:
            rels = serialize_related_identifiers(pid)
            if rels:
                result['metadata'].setdefault(
                    'related_identifiers', []).extend(rels)
        return result

    def dump(self, obj, context=None):
        """Serialize object with schema."""
        return self.schema_class(context=context).dump(obj).data

    def transform_record(self, pid, record, links_factory=None):
        """Transform record into an intermediate representation."""
        return self.dump(
            self.preprocess_record(pid, record, links_factory=links_factory),
            context={'pid': pid}
        )

    def transform_search_hit(self, pid, record_hit, links_factory=None):
        """Transform search result hit into an intermediate representation."""
        return self.dump(
            self.preprocess_search_hit(
                pid, record_hit, links_factory=links_factory),
            context={'pid': pid}
        )
