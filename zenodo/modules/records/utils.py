
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

"""Helper methods for Zenodo records."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_records.api import Record
from invenio_search import current_search
from invenio_search.utils import schema_to_index
from werkzeug.utils import import_string

from zenodo.modules.openaire import current_openaire


def schema_prefix(schema):
    """Get index prefix for a given schema."""
    if not schema:
        return None
    index, doctype = schema_to_index(
        schema, index_names=current_search.mappings.keys())
    return index.split('-')[0]


def is_record(record):
    """Determine if a record is a bibliographic record."""
    return schema_prefix(record.get('$schema')) == 'records'


def is_deposit(record):
    """Determine if a record is a deposit record."""
    return schema_prefix(record.get('$schema')) == 'deposits'


def serialize_record(record, pid, serializer, module=None, throws=True,
                     **kwargs):
    """Serialize record according to the passed serializer."""
    if isinstance(record, Record):
        try:
            module = module or 'zenodo.modules.records.serializers'
            serializer = import_string('.'.join((module, serializer)))
            return serializer.serialize(pid, record, **kwargs)
        except Exception:
            current_app.logger.exception(
                u'Record serialization failed {}.'.format(str(record.id)))
            if throws:
                raise


def is_doi_locally_managed(doi_value):
    """Determine if a DOI value is locally managed."""
    return any(doi_value.startswith(prefix) for prefix in
               current_app.config['ZENODO_LOCAL_DOI_PREFIXES'])


def is_valid_openaire_type(resource_type, communities):
    """Check if the OpenAIRE subtype is corresponding with other metadata.

    :param resource_type: Dictionary corresponding to 'resource_type'.
    :param communities: list of communities identifiers
    :returns: True if the 'openaire_subtype' (if it exists) is valid w.r.t.
        the `resource_type.type` and the selected communities, False otherwise.
    """
    if 'openaire_subtype' not in resource_type:
        return True
    oa_subtype = resource_type['openaire_subtype']
    prefix = oa_subtype.split(':')[0] if ':' in oa_subtype else ''

    cfg = current_openaire.openaire_communities
    defined_comms = [c for c in cfg.get(prefix, {}).get('communities', [])]
    type_ = resource_type['type']
    subtypes = cfg.get(prefix, {}).get('types', {}).get(type_, [])
    # Check if the OA subtype is defined in config and at least one of its
    # corresponding communities is present
    is_defined = any(t['id'] == oa_subtype for t in subtypes)
    comms_match = len(set(communities) & set(defined_comms))
    return is_defined and comms_match
