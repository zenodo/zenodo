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
from invenio_records_files.api import Record
from invenio_records_rest.serializers.json import JSONSerializer

from ..permissions import has_access


class ZenodoJSONSerializer(JSONSerializer):
    """Legacy JSON Serializer."""

    def preprocess_record(self, pid, record, links_factory=None):
        """Include files for single record retrievals."""
        result = super(JSONSerializer, self).preprocess_record(
            pid, record, links_factory=links_factory
        )
        if isinstance(record, Record) and '_files' in record:
            if not has_request_context() or has_access(current_user, record):
                result['files'] = record['_files']
        return result
