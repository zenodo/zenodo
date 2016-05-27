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

"""CLI for ZenodoJSONSchemas."""

from __future__ import absolute_import, print_function

import json

import click
from flask_cli import with_appcontext
from flask import current_app
from .compilers import compile_deposit_jsonschema, compile_record_jsonschema, \
    compile_file_jsonschema
from .utils import save_jsonschema, get_abs_schema_path


@click.group()
def jsonschemas():
    """Command for resolving jsonschemas."""


def compile_common_cli(output_file, default_file, compile_fun, schema_paths):
    """Common CLI parts of jsonschema compilation.

    If 'default_file is set to True, write to a pre-configured destination
    in current repository, alternatively if 'output_file' is set, write to a
    custom destination.

    :param output_file: Filename to which the jsonschema should be written.
    :type output_file: str
    :param default_file: Flag if the output file should be the default
                         repository jsonschema, as defined in config.
    :type default_file: bool
    :param compile_fun: Function turning old JSONSchema into a resolved one.
    :param schema_paths: A pair of jsonschema names, resolvable by
                         invenio-jsonschemas, pointing to a source
                         and destination schemas (2-tuple of strings).
    :type schema_paths: tuple
    """
    schema_path_src, schema_path_dst = schema_paths

    compiled_schema = compile_fun(schema_path_src)
    if default_file:
        abs_schema_path = get_abs_schema_path(schema_path_dst)
        if click.confirm('This will overwrite the jsonschema in this'
                         ' repository ({}). Continue?'.format(abs_schema_path),
                         default=True):
            save_jsonschema(compiled_schema, abs_schema_path)
    elif output_file:
        save_jsonschema(compiled_schema, output_file)
    else:
        click.echo(json.dumps(compiled_schema, indent=2))


@jsonschemas.command('compilerecord')
@click.option('--output_file', '-f', type=click.Path(exists=False,
              dir_okay=False))
@click.option('--default_file', '-d', is_flag=True, default=False)
@with_appcontext
def compile_record_cli(output_file, default_file):
    """Compile Zenodo record jsonschema."""
    compile_common_cli(output_file, default_file, compile_record_jsonschema,
                       current_app.config['ZENODO_JSONSCHEMAS_RECORD_SCHEMA'])


@jsonschemas.command('compiledeposit')
@click.option('--output_file', '-f', type=click.Path(exists=False,
              dir_okay=False))
@click.option('--default_file', '-d', is_flag=True, default=False)
@with_appcontext
def compile_deposit_cli(output_file, default_file):
    """Compile Zenodo deposit jsonschema."""
    compile_common_cli(output_file, default_file, compile_deposit_jsonschema,
                       current_app.config['ZENODO_JSONSCHEMAS_DEPOSIT_SCHEMA'])


@jsonschemas.command('compilefile')
@click.option('--output_file', '-f', type=click.Path(exists=False,
              dir_okay=False))
@click.option('--default_file', '-d', is_flag=True, default=False)
@with_appcontext
def compile_file_cli(output_file, default_file):
    """Compile Zenodo records file jsonschema."""
    compile_common_cli(output_file, default_file, compile_file_jsonschema,
                       current_app.config['ZENODO_JSONSCHEMAS_FILE_SCHEMA'])
