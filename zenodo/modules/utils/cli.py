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
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_records.models import RecordMetadata

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.records.resolvers import record_resolver

from .tasks import has_corrupted_files_meta, repair_record_metadata, \
    sync_record_oai, update_oaisets_cache


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
        click.echo(click.style(u'File with key "{key}" alreay exists.'
                   u' Use `--replace-existing/-f` to overwrite it.'.format(
                        key=key, recid=recid), fg='red'))
        return

    fp.seek(SEEK_SET, SEEK_END)
    size = fp.tell()
    fp.seek(SEEK_SET)

    click.echo(u'Will add the following file:\n')
    click.echo(click.style(
        u'  key: "{key}"\n'
        u'  bucket: {bucket}\n'
        u'  size: {size}\n'
        u''.format(
            key=key,
            bucket=bucket.id,
            size=size),
        fg='green'))
    click.echo(u'to record:\n')
    click.echo(click.style(
        u'  Title: "{title}"\n'
        u'  RECID: {recid}\n'
        u'  UUID: {uuid}\n'
        u''.format(
            recid=record['recid'],
            title=record['title'],
            uuid=record.id),
        fg='green'))
    if replace_existing and obj is not None:
        click.echo(u'and remove the file:\n')
        click.echo(click.style(
            u'  key: "{key}"\n'
            u'  bucket: {bucket}\n'
            u'  size: {size}\n'
            u''.format(
                key=obj.key,
                bucket=obj.bucket,
                size=obj.file.size),
            fg='green'))

    if click.confirm(u'Continue?'):
        bucket.locked = False
        if obj is not None and replace_existing:
            ObjectVersion.delete(bucket, obj.key)
        ObjectVersion.create(bucket, key, stream=fp, size=size)
        bucket.locked = True

        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style(u'File added successfully.', fg='green'))
    else:
        click.echo(click.style(u'File addition aborted.', fg='green'))


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
        click.echo(click.style(u'File with key "{key}" not found.'.format(
            key=key, recid=recid), fg='red'))
        return

    click.echo(u'Will remove the following file:\n')
    click.echo(click.style(
        u'  key: "{key}"\n'
        u'  {checksum}\n'
        u'  bucket: {bucket}\n'
        u''.format(
            key=key,
            checksum=obj.file.checksum,
            bucket=bucket.id),
        fg='green'))
    click.echo('from record:\n')
    click.echo(click.style(
        u'  Title: "{title}"\n'
        u'  RECID: {recid}\n'
        u'  UUID: {uuid}\n'
        u''.format(
            recid=record['recid'],
            title=record['title'],
            uuid=record.id),
        fg='green'))

    if click.confirm(u'Continue?'):
        bucket.locked = False
        ObjectVersion.delete(bucket, obj.key)
        bucket.locked = True
        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style(u'File removed successfully.', fg='green'))
    else:
        click.echo(click.style(u'Aborted file removal.', fg='green'))


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
        click.echo(click.style(u'File with key "{key}" not found.'.format(
            key=key), fg='red'))
        return

    new_obj = ObjectVersion.get(bucket, new_key)
    if new_obj is not None:
        click.echo(click.style(u'File with key "{key}" already exists.'.format(
            key=new_key), fg='red'))
        return

    if click.confirm(u'Rename "{key}" to "{new_key}" on bucket {bucket}.'
                     u' Continue?'.format(
                        key=obj.key, new_key=new_key, bucket=bucket.id)):
        record.files.bucket.locked = False

        file_id = obj.file.id
        ObjectVersion.delete(bucket, obj.key)
        ObjectVersion.create(bucket, new_key, _file_id=file_id)
        record.files.bucket.locked = True
        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style(u'File renamed successfully.', fg='green'))
    else:
        click.echo(click.style(u'Aborted file rename.', fg='green'))


@utils.command('list_files')
@click.argument('recid', type=str)
@with_appcontext
def list_files(recid):
    """List files for the record."""
    pid, record = record_resolver.resolve(recid)
    click.echo(u'Files for record {recid} (UUID:{uuid}) ({cnt} file(s)):\n'
               u''.format(recid=recid, uuid=record.id, cnt=len(record.files)))
    for idx, key in enumerate(record.files.keys):
        f = record.files[key].obj.file
        click.echo(click.style(
            u'{idx:3}: "{key}", {checksum}, size:{size}'
            u''.format(idx=idx, key=key, checksum=f.checksum, size=f.size),
            fg='green'))


@utils.command('sync_oai')
@click.option('--eager', '-e', is_flag=True)
@click.option('--oai-cache', is_flag=True)
@click.option('--uuid', '-i')
@with_appcontext
def sync_oai(eager, oai_cache, uuid):
    """Update OAI IDs in the records."""
    if uuid:
        sync_record_oai(str(uuid))
    else:
        pids = PersistentIdentifier.query.filter(
            PersistentIdentifier.pid_type == 'recid',
            PersistentIdentifier.object_type == 'rec',
            PersistentIdentifier.status == 'R')
        uuids = (pid.get_assigned_object() for pid in pids)
        oaisets_cache = {} if oai_cache else None
        with click.progressbar(uuids, length=pids.count()) as uuids_bar:
            for uuid in uuids_bar:
                if oai_cache:
                    rec = Record.get_record(uuid)
                    update_oaisets_cache(oaisets_cache, rec)
                if eager:
                    sync_record_oai(str(uuid), cache=oaisets_cache)
                else:
                    sync_record_oai.delay(str(uuid), cache=oaisets_cache)


@utils.command('repair_corrupted_metadata')
@click.option('--eager', '-e', is_flag=True)
@click.option('--uuid', '-i')
@with_appcontext
def repair_corrupted_metadata(eager, uuid):
    """Repair the corrupted '_files', '_oai' and '_internal' metadata."""
    if uuid:
        record = Record.get_record(uuid)
        if has_corrupted_files_meta(record):
            repair_record_metadata(str(uuid))
    else:
        rms = db.session.query(RecordMetadata).join(
            PersistentIdentifier,
            PersistentIdentifier.object_uuid == RecordMetadata.id).filter(
                PersistentIdentifier.pid_type == 'recid',
                PersistentIdentifier.status == 'R',
                PersistentIdentifier.object_type == 'rec')

        uuids = [r.id for r in rms if has_corrupted_files_meta(r.json)]
        if not click.confirm('Will update {cnt} records. Continue?'.format(
                cnt=len(uuids))):
            return
        with click.progressbar(uuids, length=len(uuids)) as uuids_bar:
            for uuid in uuids_bar:
                if eager:
                    repair_record_metadata(str(uuid))
                else:
                    repair_record_metadata.delay(str(uuid))
