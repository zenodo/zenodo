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

"""Mixin helper class for preprocessing records and search results."""

from __future__ import absolute_import, print_function

import pytz


class PreprocessorMixin(object):
    """Base class for serializers."""

    @staticmethod
    def preprocess_record(pid, record):
        """Prepare a record and persistent identifier for serialization."""
        return dict(
            pid=pid,
            metadata=record.dumps(),
            links=dict(
                self=None,
                html_url=None,
            ),
            revision=record.revision_id,
            created=(pytz.utc.localize(record.created).isoformat()
                     if record.created else None),
            updated=(pytz.utc.localize(record.updated).isoformat()
                     if record.updated else None),
        )

    @staticmethod
    def preprocess_search_hit(pid, record_hit):
        """Prepare a record hit from Elasticsearch for serialization."""
        record = dict(
            pid=pid,
            metadata=record_hit['_source'],
            links=dict(
                self=None,
                html_url=None,
            ),
            revision=record_hit['_version'],
            created=None,
            updated=None,
        )
        # Move created/updated attrs from source to object.
        for key in ['_created', '_updated']:
            if key in record['metadata']:
                record[key[1:]] = record['metadata'][key]
                del record['metadata'][key]
        return record
