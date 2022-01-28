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

import json
import os
from io import SEEK_END, SEEK_SET

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_cache import current_cache
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.errors import PIDDeletedError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_records.models import RecordMetadata

from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.openaire.helpers import openaire_datasource_id, \
    openaire_original_id, openaire_type
from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.resolvers import record_resolver

from ..openaire.tasks import _openaire_request_factory, openaire_direct_index
from ..records.resolvers import record_resolver
from .grants import OpenAIREGrantsDump
from .openaire import OpenAIRECommunitiesMappingUpdater
from .tasks import has_corrupted_files_meta, repair_record_metadata, \
    sync_record_oai, update_oaisets_cache, update_search_pattern_sets


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
    """Add a new file to a published record."""
    pid, record = record_resolver.resolve(recid)
    bucket = record.files.bucket
    key = os.path.basename(fp.name)

    obj = ObjectVersion.get(bucket, key)
    if obj is not None and not replace_existing:
        click.echo(click.style(u'File with key "{key}" already exists.'
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
            key=key.decode('utf-8'),
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
            bucket.size -= obj.file.size
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
    """Remove a file from a published record."""
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
            key=key.decode('utf-8'),
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
        bucket.size -= obj.file.size
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
    """Remove a file from a published record."""
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
        bucket.locked = False

        file_id = obj.file.id
        bucket.size -= obj.file.size
        ObjectVersion.delete(bucket, obj.key)
        ObjectVersion.create(bucket, new_key, _file_id=file_id)
        bucket.locked = True
        record.files.flush()
        record.commit()
        db.session.commit()
        click.echo(click.style(u'File renamed successfully.', fg='green'))
    else:
        click.echo(click.style(u'Aborted file rename.', fg='green'))


@utils.command('attach_file')
@click.option('--file-id', type=str)
@click.option('--pid-type1', type=str)
@click.option('--pid-value1', type=str)
@click.option('--key1', type=str)
@click.option('--pid-type2', type=str)
@click.option('--pid-value2', type=str)
@click.option('--key2', type=str)
@with_appcontext
def attach_file(file_id, pid_type1, pid_value1, key1, pid_type2, pid_value2,
                key2):
    """Attach a file to a record or deposit.

    You must provide the information which will determine the first file, i.e.:
    either 'file-id' OR 'pid-type1', 'pid-value1' and 'key1'.
    Additionally you need to specify the information on the target
    record/deposit, i.e.: 'pid-type2', 'pid-value2' and 'key2'.
    """
    assert ((file_id or (pid_type1 and pid_value1 and key1))
            and (pid_type2 and pid_value2 and key2))

    msg = u"PID type must be 'recid' or 'depid'."
    if pid_type1:
        assert pid_type1 in ('recid', 'depid', ), msg
    assert pid_type2 in ('recid', 'depid', ), msg

    if not file_id:
        resolver = record_resolver if pid_type1 == 'recid' \
            else deposit_resolver
        pid1, record1 = resolver.resolve(pid_value1)
        bucket1 = record1.files.bucket

        obj1 = ObjectVersion.get(bucket1, key1)
        if obj1 is None:
            click.echo(click.style(u'File with key "{key}" not found.'.format(
                key=key1), fg='red'))
            return
        file_id = obj1.file.id

    resolver = record_resolver if pid_type2 == 'recid' else deposit_resolver
    pid2, record2 = resolver.resolve(pid_value2)
    bucket2 = record2.files.bucket

    obj2 = ObjectVersion.get(bucket2, key2)
    if obj2 is not None:
        click.echo(click.style(u'File with key "{key}" already exists on'
                               u' bucket {bucket}.'.format(
                                   key=key2, bucket=bucket2.id), fg='red'))
        return

    if click.confirm(u'Attaching file "{file_id}" to bucket {bucket2}'
                     u' as "{key2}". Continue?'.format(
                         file_id=file_id, key2=key2,
                         bucket2=bucket2.id)):
        record2.files.bucket.locked = False

        ObjectVersion.create(bucket2, key2, _file_id=file_id)
        if pid_type2 == 'recid':
            record2.files.bucket.locked = True
        record2.files.flush()
        record2.commit()
        db.session.commit()
        click.echo(click.style(u'File attached successfully.', fg='green'))
    else:
        click.echo(click.style(u'Aborted file attaching.', fg='green'))


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


@utils.command('update_search_pattern_sets')
@with_appcontext
def update_search_pattern_sets_cli():
    """Update records belonging to all search-pattern OAISets."""
    update_search_pattern_sets.delay()


@utils.command('split_openaire_grants_dump')
@click.argument('source', type=click.Path(exists=True, dir_okay=False))
@click.argument('target_prefix')
@click.option('--grants-per-file', '-n', type=int, default=None)
@click.option('--sqlite-write-rows-buffer', type=int, default=None)
@with_appcontext
def split_openaire_grants_dump(source, target_prefix, grants_per_file=None,
                               sqlite_write_rows_buffer=None):
    """Split an OpenAIRE grants dump into multiple SQLite files.

    The file can then be imported via ``zenodo openaire loadgrants ...``.
    """
    grants_dump = OpenAIREGrantsDump(
        source, rows_write_chunk_size=sqlite_write_rows_buffer)
    split_files = grants_dump.split(
        target_prefix, grants_per_file=grants_per_file)
    total_rows = 0
    for filepath, row_count in split_files:
        total_rows += row_count
        click.secho('{0} - {1} (Total: {2})'
                    .format(filepath, row_count, total_rows),
                    fg='blue')


@utils.command('update_openaire_communities')
@click.argument('path', type=click.Path(exists=True, dir_okay=False))
@with_appcontext
def update_openaire_communities(path):
    """Get the updated mapping between OpenAIRE and Zenodo communities."""
    mapping_updater = OpenAIRECommunitiesMappingUpdater(path)
    mapping, unresolved_communities = mapping_updater\
        .update_communities_mapping()
    click.secho('Communities not found:\n{0}'.format(json.dumps(
        unresolved_communities, indent=4, separators=(', ', ': '))))
    click.secho('{0}'.format(json.dumps(mapping, indent=4,
                                        separators=(', ', ': '))), fg='blue')

def _iter_openaire_direct_index_keys():
    return current_cache.cache._read_clients.scan_iter(
        match=(current_cache.cache.key_prefix + 'openaire_direct_index*'))

@utils.command('list_failed_openaire_records')
@with_appcontext
def list_failed_openaire_records():
    """Lists records that failed to get indexed in OpenAIRE."""
    failed_record_recids = []
    for key in _iter_openaire_direct_index_keys():
        recid = key.split('openaire_direct_index:')[1]
        failed_record_recids.append(key)
    click.echo('\n'.join(failed_record_recids))


@utils.command('index_or_delete_openaire_records')
@click.option('--eager', '-e', default=False)
@with_appcontext
def retry_indexing_or_delete_openaire_records(eager):
    """Retries indexing/deleting records that failed to get indexed/deleted
    in OpenAIRE."""
    for key in _iter_openaire_direct_index_keys():
        recid = key.split('openaire_direct_index:')[1]

        try:
            recid, record  = record_resolver.resolve(recid)

        except PIDDeletedError:
            record_data = PersistentIdentifier.query.filter_by(
                pid_type="recid", pid_value=str(recid), status=PIDStatus.DELETED
            ).one()
            record = ZenodoRecord.get_record(
                    record_data.object_uuid, with_deleted=True
                    )

            try:
                index = -2
                last_valid_revision = record.revisions[index]
                while "resource_type" not in last_valid_revision:
                    last_valid_revision = record.revisions[index]
                    index = index -1

            except:
                click.echo("The record with id {} does not have a valid \
                            last_valid_revision".format(recid))
                continue

            original_id = openaire_original_id(
                last_valid_revision, openaire_type(last_valid_revision)
            )[1]
            datasource_id = openaire_datasource_id(last_valid_revision)

            click.echo("Deleting record with id {}".format(record_data))
            openaire_delete(
                str(record_data.object_uuid), original_id, datasource_id
            )
            continue

        click.echo("Indexing record with id {}".format(recid))
        if eager:
            openaire_direct_index(str(recid.object_uuid), retry=False)
        else:
            openaire_direct_index.delay(
                str(recid.object_uuid), retry=False)
