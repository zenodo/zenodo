# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile

import pytest
from elasticsearch.exceptions import RequestError
from flask_cli import ScriptInfo
from invenio_db import db as db_
from invenio_search import current_search
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from zenodo.factory import create_app


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    os.environ.update(
        APP_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )

    app = create_app(
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )

    def teardown():
        shutil.rmtree(instance_path)

    request.addfinalizer(teardown)

    with app.app_context():
        yield app


@pytest.yield_fixture(scope='session')
def script_info(app):
    """Ensure that the database schema is created."""
    yield ScriptInfo(create_app=lambda info: app)


@pytest.yield_fixture(scope='session')
def database(app):
    """Ensure that the database schema is created."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.drop_all()
    db_.create_all()

    yield db_

    drop_database(str(db_.engine.url))


@pytest.yield_fixture(scope='session')
def es(app):
    """Provide elasticsearch access."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete())
        list(current_search.create())
    yield current_search
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture
def db(database, monkeypatch):
    """Provide database access and ensure changes do not persist."""
    # Prevent database/session modifications
    monkeypatch.setattr(database.session, 'commit', database.session.flush)
    monkeypatch.setattr(database.session, 'remove', lambda: None)
    yield database
    database.session.rollback()
    database.session.remove()
