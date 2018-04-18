# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016, 2017 CERN.
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

import json
from os.path import dirname, join

import click
from flask.cli import with_appcontext
from invenio_communities.models import Community
from invenio_communities.utils import initialize_communities_bucket
from invenio_db import db
from invenio_openaire.minters import funder_minter, grant_minter
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record

from .communities import loadcommunity
from .files import loadbuckets, loaddemofiles, loadlocations
from .licenses import loadlicenses, matchlicenses
from .oai import loadoaisets
from .records import loaddemorecords, loadsipmetadatatypes
from .users import loaduser
from .utils import read_json


@click.group()
def fixtures():
    """Command for loading fixture data."""


@fixtures.command()
@with_appcontext
def init():
    """Load basic data."""
    loadlocations()
    loadbuckets()
    loadoaisets()
    initialize_communities_bucket()


@fixtures.command('loadlocations')
@with_appcontext
def loadlocations_cli():
    """Load data store location."""
    locs = loadlocations()
    click.secho('Created location(s): {0}'.format(
        [loc.uri for loc in locs]), fg='green')


@fixtures.command('loadoaisets')
@with_appcontext
def loadoaisets_cli():
    """Load OAI-PMH sets."""
    sets_count = loadoaisets()
    click.secho('Created {0} OAI-PMH sets'.format(len(sets_count)), fg='green')


@fixtures.command('loadfp6grants')
@with_appcontext
def loadfp6grants_cli():
    """Load one-off grants."""
    data = read_json('data/grants.json')
    loaded = 0
    for g in data:
        if not PersistentIdentifier.query.filter_by(
                pid_type='grant', pid_value=g['internal_id']).count():
            r = Record.create(g)
            grant_minter(r.id, r)
            db.session.commit()
            loaded += 1
    click.echo("Loaded {0} new grants out of {1}.".format(loaded, len(data)))


@fixtures.command('loadfunders')
@with_appcontext
def loadfunders_cli():
    """Load the supported funders."""
    data = read_json('data/funders.json')
    loaded = 0
    for f in data:
        if not PersistentIdentifier.query.filter_by(
                pid_type='frdoi', pid_value=f['doi']).count():
            r = Record.create(f)
            funder_minter(r.id, r)
            db.session.commit()
            loaded += 1
    click.echo("Loaded {0} new funders out of {1}.".format(loaded, len(data)))


@fixtures.command('loaddemorecords')
@with_appcontext
def loaddemorecords_cli():
    """Load demo records."""
    click.echo('Loading demo data...')
    with open(join(dirname(__file__), 'data/records.json'), 'r') as fp:
        data = json.load(fp)

    click.echo('Sending tasks to queue...')
    with click.progressbar(data) as records:
        loaddemorecords(records)

    click.echo("1. Start Celery:")
    click.echo("     celery worker -A zenodo.celery -l INFO")
    click.echo("2. After tasks have been processed start reindexing:")
    click.echo("     zenodo migration recordsrun")
    click.echo("     zenodo index reindex -t recid")
    click.echo("     zenodo index run -d -c 4")


@fixtures.command('loadsipmetadatatypes')
@with_appcontext
def loadsipmetadatatypes_cli():
    """Load SIP metadata types."""
    click.secho('Loading SIP metadata types...', fg='blue')
    src = join(dirname(__file__), 'data/sipmetadatatypes.json')
    with open(src, 'r') as fp:
        data = json.load(fp)
    with click.progressbar(data) as types:
        loadsipmetadatatypes(types)
    click.secho('SIP metadata types loaded!', fg='green')


@fixtures.command('loaddemofiles')
@click.argument('source', type=click.Path(exists=True, dir_okay=False,
                                          resolve_path=True))
@with_appcontext
def loaddemofiles_cli(source):
    """Load demo files."""
    loaddemofiles(source)


@fixtures.command('loadlicenses')
@with_appcontext
def loadlicenses_cli():
    """Load Zenodo licenses."""
    loadlicenses()


@fixtures.command('matchlicenses')
@click.argument('legacy_source', type=click.Path(exists=True, dir_okay=False,
                                                 resolve_path=True))
@click.argument('od_source', type=click.Path(exists=True, dir_okay=False,
                                             resolve_path=True))
@click.argument('destination', type=click.Path(exists=False, dir_okay=False))
def matchlicenses_cli(legacy_source, od_source, destination):
    """Match legacy Zenodo licenses with OpenDefinition.org licenses."""
    matchlicenses(legacy_source, od_source, destination)


@fixtures.command('loadcommunities')
@click.option('-i', '--input-file')
@with_appcontext
def loadcommunities_cli(input_file=None):
    """Load Zenodo communities."""
    data = read_json(input_file or 'data/communities.json')
    skipped = 0
    for comm_data in data:
        if not Community.query.filter_by(id=comm_data['id']).count():
            loadcommunity(comm_data)
        else:
            skipped += 1

    click.secho('Loaded {0} communities (skipped {1} existing).'.format(
        len(data) - skipped, skipped), fg='green')


@fixtures.command('loadusers')
@click.option('-i', '--input-file')
@with_appcontext
def loadusers_cli(input_file=None):
    """Load Zenodo users."""
    users = read_json(input_file or 'data/users.json')
    for user_data in users:
        loaduser(user_data)
