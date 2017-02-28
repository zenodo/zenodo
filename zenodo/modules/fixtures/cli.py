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

import json
from os.path import dirname, join

import click
from flask.cli import with_appcontext
from invenio_communities.utils import initialize_communities_bucket
from sqlalchemy.orm.exc import NoResultFound

from .communities import loadcommunities
from .files import loaddemofiles, loadlocation
from .grants import loadfp6funders, loadfp6grants
from .licenses import loadlicenses, matchlicenses
from .oai import loadoaisets
from .pages import loadpages
from .records import loaddemorecords


@click.group()
def fixtures():
    """Command for loading fixture data."""


@fixtures.command()
@with_appcontext
def init():
    """Load basic data."""
    loadpages()
    loadlocation()
    loadoaisets()
    initialize_communities_bucket()


@fixtures.command('loadpages')
@click.option('--force', '-f', is_flag=True, default=False)
@with_appcontext
def loadpages_cli(force):
    """Load pages."""
    loadpages(force=force)
    click.secho('Created pages', fg='green')


@fixtures.command('loadlocation')
@with_appcontext
def loadlocation_cli():
    """Load data store location."""
    loc = loadlocation()
    click.secho('Created location {0}'.format(loc.uri), fg='green')


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
    loadfp6grants()


@fixtures.command('loadfp6funders')
@with_appcontext
def loadfp6funders_cli():
    """Load one-off funders."""
    loadfp6funders()


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
    click.echo("     zenodo migration reindex recid")
    click.echo("     zenodo index run -d -c 4")


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
@click.argument('owner_email')
@with_appcontext
def loadcommunities_cli(owner_email):
    """Load Zenodo communities."""
    try:
        loadcommunities(owner_email)
    except NoResultFound:
        click.echo("Error: Provided owner email does not exist.")
