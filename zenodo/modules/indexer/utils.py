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

"""Zenodo-specific InvenioIndexer utility functions."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_indexer.utils import default_record_to_index

from elasticsearch import VERSION as ES_VERSION

def record_to_index(record):
    """Get the elasticsearch index and doc_type for given record.

    Construct the index name from the `record['$schema']`, which is then
    mapped with an elastisearch document type (fixed difinition in the config).

    :param record: The record object.
    :type record: `invenio_records.api.Record`
    :returns: Tuple of (index, doc_type)
    :rtype: (str, str)
    """
    if ES_VERSION[0] < 7:
        index, doc_type = default_record_to_index(record)
    if ES_VERSION[0] >= 7:
        index, doc_type = default_record_to_index(record)
        doc_type = '_doc'

    return index, current_app.config['INDEXER_SCHEMA_TO_INDEX_MAP'].get(
        index, doc_type)
