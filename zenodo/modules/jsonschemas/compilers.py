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

"""JSON schema compiler methods."""

from __future__ import absolute_import, print_function

from .utils import merge_dicts, remove_keys, replace_schema_refs, \
    resolve_schema_path, resolve_schema_url


def _iter_all_of(schema):
    """Iterate over the items within schema 'allOf' definition at the root."""
    if 'allOf' in schema:
        for sub_schema_ref in schema['allOf']:
            sub_schema_url = sub_schema_ref['$ref']
            sub_schema = resolve_schema_url(sub_schema_url)
            yield sub_schema


def _compile_common(schema):
    """Compile common parts for record and deposit."""
    id_ = schema['id']
    title = schema['title']
    # We need to iter 'allOf' manually because jsonresolver
    # will not preserve ordering of subschema keys
    for sub_schema in _iter_all_of(schema):
        schema = merge_dicts(schema, sub_schema)
    schema = replace_schema_refs(schema)
    if 'allOf' in schema:
        del schema['allOf']
    schema['id'] = id_
    schema['title'] = title
    return schema


def _compile_deposit_base(schema):
    """Compile the base deposition jsonschema."""
    deposit_base_schema = schema['allOf'][0]
    assert 'deposits/deposit' in deposit_base_schema['$ref']
    base_dep_schema = resolve_schema_url(deposit_base_schema['$ref'])
    del base_dep_schema['properties']['_files']
    schema = merge_dicts(base_dep_schema, schema)
    schema['allOf'] = schema['allOf'][1:]
    return schema


def compile_deposit_jsonschema(schema_path):
    """Compile the deposit jsonschema."""
    schema = resolve_schema_path(schema_path)
    schema = _compile_deposit_base(schema)
    schema = _compile_common(schema)
    schema['properties'] = remove_keys(schema['properties'], ['required', ])
    return schema


def compile_record_jsonschema(schema_path):
    """Compile the record jsonschema."""
    compiled = resolve_schema_path(schema_path)
    compiled = _compile_deposit_base(compiled)
    compiled = _compile_common(compiled)
    del compiled['description']  # Description inherited from deposit
    return compiled


def compile_file_jsonschema(schema_path):
    """Compile file jsonschema."""
    compiled = resolve_schema_path(schema_path)
    # We need to iter 'allOf' manually because jsonresolver
    # will not preserve ordering of subschema keys
    file_url = compiled['properties']['_files']['items']['allOf'][0]['$ref']
    file_base = resolve_schema_url(file_url)
    file_extra = compiled['properties']['_files']['items']['allOf'][1]
    file_items = merge_dicts(file_base, file_extra)
    del file_items['$schema']
    del file_items['title']
    del compiled['properties']['_files']['items']['allOf']
    compiled['properties']['_files']['items'] = file_items
    return compiled
