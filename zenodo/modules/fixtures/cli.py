# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""CLI for Zenodo fixtures."""

from __future__ import absolute_import, print_function

import hashlib
import json
from os import makedirs, stat
from os.path import dirname, exists, join

import click
from celery import chain
from flask import current_app
from flask_cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import FileInstance, Location, ObjectVersion
from invenio_migrator.proxies import current_migrator
from invenio_migrator.tasks.records import import_record
from invenio_oaiserver.models import OAISet
from invenio_openaire.minters import grant_minter
from invenio_pages.models import Page
from invenio_records.api import Record
from pkg_resources import resource_stream, resource_string


def _read_json(path):
    """Retrieve JSON from package resource."""
    return json.loads(
        resource_string('zenodo.modules.fixtures', path).decode('utf8'))


def _file_stream(path):
    """Retrieve JSON from package resource."""
    return resource_stream('zenodo.modules.fixtures', path)


@click.group()
def fixtures():
    """Command for loading fixture data."""


@fixtures.command()
@click.option('--force', '-f', is_flag=True, default=False)
@with_appcontext
def loadpages(force):
    """Load pages."""
    data = _read_json('data/pages.json')

    try:
        if force:
            Page.query.delete()
        for p in data:
            if len(p['description']) >= 200:
                raise ValueError(  # pragma: nocover
                    "Description too long for {0}".format(p['url']))
            p = Page(
                url=p['url'],
                title=p['title'],
                description=p['description'],
                content=_file_stream(
                    join('data', p['file'])).read().decode('utf8'),
                template_name=p['template_name'],
            )
            db.session.add(p)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@fixtures.command()
@with_appcontext
def loadlocation():
    """Load data store location."""
    try:
        uri = current_app.config['FIXTURES_FILES_LOCATION']
        if not exists(uri):
            makedirs(uri)
        loc = Location(name='local', uri=uri, default=True, )
        db.session.add(loc)
        db.session.commit()
        click.secho('Created location {0}'.format(loc.uri), fg='green')
    except Exception:
        db.session.rollback()
        raise


@fixtures.command()
@with_appcontext
def loadoaisets():
    """Load OAI-PMH sets."""
    sets = [
        ('openaire', 'OpenAIRE', None),
        ('openaire_data', 'OpenAIRE data sets', None),
        ('user-zenodo', 'Zenodo', None),
    ]
    try:
        for setid, name, pattern in sets:
            oset = OAISet(spec=setid, name=name, search_pattern=pattern)
            db.session.add(oset)
        db.session.commit()
        click.secho('Created {0} OAI-PMH sets'.format(len(sets)), fg='green')
    except Exception:
        db.session.rollback()
        raise


@fixtures.command()
@with_appcontext
def loadoneoffs():
    """Load one-off grants."""
    data = _read_json('data/grants.json')
    try:
        for g in data:
            r = Record.create(g)
            grant_minter(r.id, r)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@fixtures.command()
@with_appcontext
def loaddemorecords():
    """Load demo records."""
    click.echo('Loading demo data...')
    with open(join(dirname(__file__), 'data/records.json'), 'r') as fp:
        data = json.load(fp)

    click.echo('Sending tasks to queue...')
    with click.progressbar(data) as records:
        for item in records:
            if current_migrator.records_post_task:
                chain(
                    import_record.s(item, source_type='json'),
                    current_migrator.records_post_task.s()
                )()
            else:
                import_record.delay(item, source_type='json')

    click.echo("1. Start Celery:")
    click.echo("     celery worker -A zenodo.celery -l INFO")
    click.echo("2. After tasks have been processed start reindexing:")
    click.echo("     zenodo migration reindex recid")
    click.echo("     zenodo index run -d -c 4")


@fixtures.command()
@click.argument('source', type=click.Path(exists=True, dir_okay=False,
                resolve_path=True))
@with_appcontext
def loaddemofiles(source):
    """Load demo files."""
    s = stat(source)

    with open(source, 'rb') as fp:
        m = hashlib.md5()
        m.update(fp.read())
        checksum = "md5:{0}".format(m.hexdigest())

    # Create a file instance
    with db.session.begin_nested():
        f = FileInstance.create()
        f.set_uri(source, s.st_size, checksum)

    # Replace all objects associated files.
    ObjectVersion.query.update({ObjectVersion.file_id: str(f.id)})
    db.session.commit()
