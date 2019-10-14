
# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017, 2018 CERN.
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

from os.path import dirname, join

from flask import current_app
from invenio_db import db
from invenio_indexer.utils import schema_to_index
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search
from lxml import etree
from sqlalchemy import or_
from werkzeug.utils import import_string

from zenodo.modules.openaire import current_openaire
from zenodo.modules.records import current_custom_metadata


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


def transform_record(record, pid, serializer, module=None, throws=True,
                     **kwargs):
    """Transform a record using a serializer."""
    if isinstance(record, Record):
        try:
            module = module or 'zenodo.modules.records.serializers'
            serializer = import_string('.'.join((module, serializer)))
            return serializer.transform_record(pid, record, **kwargs)
        except Exception:
            current_app.logger.exception(
                u'Record transformation failed {}.'.format(str(record.id)))
            if throws:
                raise


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


def find_registered_doi_pids(from_date, until_date, prefixes):
    """Find all local DOI's which are in the REGISTERED state."""
    query = db.session.query(PersistentIdentifier).filter(
        PersistentIdentifier.pid_type == 'doi',
        PersistentIdentifier.status == PIDStatus.REGISTERED,
        PersistentIdentifier.updated.between(from_date, until_date)
    )

    query.filter(or_(PersistentIdentifier.pid_value.like(prefix + '%') for prefix in prefixes))

    query.order_by(PersistentIdentifier.updated)

    return query


def xsd41():
    """Load DataCite v4.1 full example as an etree."""
    from zenodo.modules.records.httpretty_mock import httpretty

    # Ensure the schema validator doesn't make any http requests.
    with open(join(dirname(__file__), 'data', 'xml.xsd')) as fp:
        xmlxsd = fp.read()

    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET,
        'https://www.w3.org/2009/01/xml.xsd',
        body=xmlxsd)

    yield etree.XMLSchema(
        file='file://' + join(dirname(__file__), 'data', 'metadata41.xsd')
    )

    httpretty.disable()


def build_record_custom_fields(record):
    """Build the custom metadata fields for ES indexing."""
    valid_terms = current_custom_metadata.terms
    es_custom_fields = dict(
        custom_keywords=[],
        custom_text=[]
    )
    custom_fields_mapping = {
        'keyword': 'custom_keywords',
        'text': 'custom_text',
    }

    custom_metadata = record.get('custom', {})
    for term, value in custom_metadata.items():
        term_type = valid_terms.get(term)['term_type']
        if term_type:
            # TODO: in the future also add "community"
            es_object = {'key': term, 'value': value}
            es_custom_field = custom_fields_mapping[term_type]
            es_custom_fields[es_custom_field].append(es_object)

    return {k: es_custom_fields[k] for k in es_custom_fields
            if es_custom_fields[k]}
