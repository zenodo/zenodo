# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests Zenodo JSON schemas."""

from __future__ import absolute_import, print_function

from zenodo.modules.jsonschemas.compilers import compile_record_jsonschema, \
    compile_deposit_jsonschema, compile_file_jsonschema
from zenodo.modules.jsonschemas.utils import resolve_schema_path


def test_compile_schemas(app):
    """Test record jsonschema compilation.

    NOTE: Failure of this test most likely means that the 'compiled'
    jsonschemas have been edited manually and are divergent from the
    'source' jsonschemas.
    """
    config_vars = [
        app.config['ZENODO_JSONSCHEMAS_FILE_SCHEMA'],
        app.config['ZENODO_JSONSCHEMAS_RECORD_SCHEMA'],
        app.config['ZENODO_JSONSCHEMAS_DEPOSIT_SCHEMA'],
    ]
    compile_funcs = [
        compile_file_jsonschema,
        compile_record_jsonschema,
        compile_deposit_jsonschema,
    ]
    for config_var, compile_func in zip(config_vars, compile_funcs):
        src, dst = config_var
        compiled_schema = compile_func(src)
        repo_schema = resolve_schema_path(dst)
        assert compiled_schema == repo_schema
