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

"""Jinja utilities for Invenio."""

from __future__ import absolute_import, print_function

import json
from os import makedirs
from os.path import exists, join

import click
from flask import current_app
from flask_cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_pages.models import Page
from pkg_resources import resource_string


def _read_json(path):
    """Retrieve JSON from package resource."""
    return json.loads(_read_file(path))


def _read_file(path):
    """Retrieve JSON from package resource."""
    return resource_string(
        'zenodo.modules.fixtures',
        path).decode('utf8')


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
                content=_read_file(join("data", p['file'])),
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
