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

"""CLI for Zenodo-specific tasks."""

from __future__ import absolute_import, print_function

import os
from io import SEEK_END, SEEK_SET

import click
from flask_cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import ObjectVersion

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.records.api import record_resolver


@click.group()
def utils():
    """Zenodo helper CLI."""


@utils.command('datacite_register')
@click.argument('recid', type=str)
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def datecite_register(recid, eager):
    """Send a record to DataCite for registration."""
    pid, record = record_resolver.resolve(recid)
    if eager:
        datacite_register.s(pid.pid_value, str(record.id)).apply(throw=True)
    else:
        datacite_register.s(pid.pid_value, str(record.id)).apply_async()


@utils.command('add_file')
@click.argument('recid', type=str)
@click.argument('fp', type=click.File('rb'))
@click.option('--replace-existing', '-f', is_flag=True, default=False)
@with_appcontext
def add_file(recid, fp, replace_existing):
    """Add a new file to a publishd record."""
    pid, record = record_resolver.resolve(recid)
    bucket = record.files.bucket
    key = os.path.basename(fp.name)

    obj = ObjectVersion.get(bucket, key)
    if obj is not None and not replace_existing:
        click.echo(click.style('File with key "{key}" alreay exists.'
                   ' Use `--replace-existing/-f` to overwrite it.'.format(
                        key=key, recid=recid), fg='red'))
        return

    fp.seek(SEEK_SET, SEEK_END)
    size = fp.tell()
    fp.seek(SEEK_SET)

    click.echo('Will add the following file:\n')
    click.echo(click.style(
        '  key: "{key}"\n'
        '  bucket: {bucket}\n'
        '  size: {size}\n'
        ''.format(
            key=key,
            bucket=bucket.id,
            size=size),
        fg='orange'))
    click.echo('to record:\n')
    click.echo(click.style(
        '  Title: "{title}"\n'
        '  RECID: {recid}\n'
        '  UUID: {uuid}\n'
        ''.format(
            recid=record['recid'],
            title=record['title'],
            uuid=record.id),
        fg='green'))
    if replace_existing and obj is not None:
        click.echo('and remove the file:\n')
        click.echo(click.style(
            '  key: "{key}"\n'
            '  bucket: {bucket}\n'
            '  size: {size}\n'
            ''.format(
                key=obj.key,
                bucket=obj.bucket,
                size=obj.file.size),
            fg='green'))

    if click.confirm('Continue?'):
        bucket.locked = False
        if obj is not None and replace_existing:
            ObjectVersion.delete(bucket, obj.key)
        ObjectVersion.create(bucket, key, stream=fp)
        bucket.locked = True

        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style('File added successfully.', fg='green'))
    else:
        click.echo(click.style('File addition aborted.', fg='green'))


@utils.command('remove_file')
@click.argument('recid', type=str)
@click.argument('key', type=str)
@with_appcontext
def remove_file(recid, key=None, index=None):
    """Remove a file from a publishd record."""
    pid, record = record_resolver.resolve(recid)
    bucket = record.files.bucket
    obj = ObjectVersion.get(bucket, key)
    if obj is None:
        click.echo(click.style('File with key "{key}" not found.'.format(
            key=key, recid=recid), fg='red'))
        return

    click.echo('Will remove the following file:\n')
    click.echo(click.style(
        '  key: "{key}"\n'
        '  {checksum}\n'
        '  bucket: {bucket}\n'
        ''.format(
            key=key,
            checksum=obj.file.checksum,
            bucket=bucket.id),
        fg='green'))
    click.echo('from record:\n')
    click.echo(click.style(
        '  Title: "{title}"\n'
        '  RECID: {recid}\n'
        '  UUID: {uuid}\n'
        ''.format(
            recid=record['recid'],
            title=record['title'],
            uuid=record.id),
        fg='green'))

    if click.confirm('Continue?'):
        bucket.locked = False
        ObjectVersion.delete(bucket, obj.key)
        bucket.locked = True
        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style('File removed successfully.', fg='green'))
    else:
        click.echo(click.style('Aborted file removal.', fg='green'))


@utils.command('rename_file')
@click.argument('recid', type=str)
@click.argument('key', type=str)
@click.argument('new_key', type=str)
@with_appcontext
def rename_file(recid, key, new_key):
    """Remove a file from a publishd record."""
    pid, record = record_resolver.resolve(recid)
    bucket = record.files.bucket

    obj = ObjectVersion.get(bucket, key)
    if obj is None:
        click.echo(click.style('File with key "{key}" not found.'.format(
            key=key), fg='red'))
        return

    new_obj = ObjectVersion.get(bucket, new_key)
    if new_obj is not None:
        click.echo(click.style('File with key "{key}" already exists.'.format(
            key=new_key), fg='red'))
        return

    if click.confirm('Rename "{key}" to "{new_key}" on bucket {bucket}.'
                     ' Continue?'.format(
                        key=obj.key, new_key=new_key, bucket=bucket.id)):
        record.files.bucket.locked = False

        file_id = obj.file.id
        ObjectVersion.delete(bucket, obj.key)
        ObjectVersion.create(bucket, new_key, _file_id=file_id)
        record.files.bucket.locked = True
        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style('File renamed successfully.', fg='green'))
    else:
        click.echo(click.style('Aborted file rename.', fg='green'))


@utils.command('list_files')
@click.argument('recid', type=str)
@with_appcontext
def list_files(recid):
    """List files for the record."""
    pid, record = record_resolver.resolve(recid)
    click.echo('Files for record {recid} (UUID:{uuid}) ({cnt} file(s)):\n'
               ''.format(recid=recid, uuid=record.id, cnt=len(record.files)))
    for idx, key in enumerate(record.files.keys):
        f = record.files[key].obj.file
        click.echo(click.style(
            '{idx:3}: "{key}", {checksum}, size:{size}'
            ''.format(idx=idx, key=key, checksum=f.checksum, size=f.size),
            fg='green'))
