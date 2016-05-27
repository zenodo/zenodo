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

"""ZenodoJSONSchemas utilities functions."""

from __future__ import absolute_import, print_function
import json
from copy import deepcopy

from flask import current_app
from werkzeug.local import LocalProxy
current_jsonschemas = LocalProxy(
    lambda: current_app.extensions['invenio-jsonschemas']
)

_records_state = LocalProxy(lambda: current_app.extensions['invenio-records'])


def resolve_schema_path(schema_path):
    """Resolve a schema by name.

    Resolve a schema by it's registered name, e.g. 'records/record-v1.0.0.json'

    WARNING: This method returns a deepcopy of the original schema.
             Always use this method, as any modifications to a resolved schema
             will be retain at the application level!

    :param schema_path: schema path, e.g.: 'records/record-v1.0.0.json'.
    :type schema_path: str
    :returns: JSON schema
    :rtype: dict
    """
    schema = current_jsonschemas.get_schema(schema_path)
    return deepcopy(schema)


def resolve_schema_url(schema_url):
    """Resolve a schema url to a dict.

    WARNING: This method returns a deepcopy of the original schema.
             Always use this method, as any modifications to a resolved schema
             will be retain at the application level!

    :param schema_url: absolute url of schema, e.g.:
                       'https://zenodo.org/schemas/records/record-v1.0.0.json'.
    :type schema_url: str
    :returns: JSON schema
    :rtype: dict
    """
    schema_path = current_jsonschemas.url_to_path(schema_url)
    return resolve_schema_path(schema_path)


def replace_schema_refs(schema):
    """Replace all the refs in jsonschema.

    :param schema: JSON schema for which the refs should be resolved.
    :type schema: dict
    :returns: JSON schema with resolved refs.
    :rtype: dict
    """
    return deepcopy(_records_state.replace_refs(schema))


def get_abs_schema_path(schema_path):
    """Resolve absolute schema path on disk from schema name.

    Resolve schema name to an absolute schema path on disk, e.g.:
    'records/record-v1.0.0.json' could resolve to
    '/absolute/path/schemas/records/record-v1.0.0.json'
    """
    return current_jsonschemas.get_schema_path(schema_path)


def save_jsonschema(schema, path):
    """Save jsonschema to disk path."""
    with open(path, 'w') as fp:
        json.dump(schema, fp, indent=2, sort_keys=True)


def merge_dicts(first, second):
    """Merge the 'second' multiple-dictionary into the 'first' one."""
    new = deepcopy(first)
    for k, v in second.items():
        if isinstance(v, dict) and v:
            ret = merge_dicts(new.get(k, dict()), v)
            new[k] = ret
        else:
            new[k] = second[k]
    return new


def remove_keys(d, keys):
    """Remove keys from a dictionary (nested).

    :param d: dictionary from which the keys are to be removed.
    :type d: dict
    :param keys: keys to be removed (list of str)
    :type keys: list
    """
    if isinstance(d, dict):
        return dict((k, remove_keys(v, keys)) for k, v in d.items()
                    if k not in keys)
    elif isinstance(d, list):
        return list(remove_keys(i, keys) for i in d)
    else:
        return d
