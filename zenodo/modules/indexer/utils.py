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
from invenio_search import current_search
from invenio_search.utils import schema_to_index


def record_to_index(record):
    """Get the elasticsearch index and doc_type for given record.

    Construct the index name from the `record['$schema']`, which is then
    mapped with an elastisearch document type (fixed difinition in the config).

    :param record: The record object.
    :type record: `invenio_records.api.Record`
    :returns: Tuple of (index, doc_type)
    :rtype: (str, str)
    """
    schema2index_map = current_app.config['INDEXER_SCHEMA_TO_INDEX_MAP']
    index_names = current_search.mappings.keys()

    schema = record.get('$schema', '')
    if isinstance(schema, dict):
        schema = schema.get('$ref', '')

    if not schema:
        raise Exception ("Record '{uuid}' does not specify a '$schema' key "
            "in metadata.".format(uuid=record.id))

    index, _ = schema_to_index(schema, index_names=index_names)

    if index not in schema2index_map:
        raise Exception ("Dictionary between schemas and index mappings "
            "is not exhaustive ({index} not in {mapping}).".format(
                index=index, mapping=schema2index_map))
    doc_type = schema2index_map[index]

    return index, doc_type
