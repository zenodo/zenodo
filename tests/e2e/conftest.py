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

"""Pytest configuration.

Before running any of the tests you must have initialized the assets using
the ``script scripts/setup-assets.sh``.
"""

from __future__ import absolute_import, print_function

import os

import pytest
from invenio_db import db
from invenio_search import current_search
from selenium import webdriver
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from zenodo.factory import create_app


@pytest.fixture()
def app(request):
    """Flask application fixture."""
    app = create_app(
        CELERY_ALWAYS_EAGER=True,
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        CELERY_RESULT_BACKEND="cache",
        DEBUG_TB_ENABLED=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME",
        MAIL_SUPPRESS_SEND=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )

    with app.app_context():
        if not database_exists(str(db.engine.url)):
            create_database(str(db.engine.url))
        db.drop_all()
        db.create_all()
        list(current_search.create())

    def teardown():
        with app.app_context():
            drop_database(str(db.engine.url))
            list(current_search.delete(ignore=[404]))

    request.addfinalizer(teardown)

    return app


def pytest_generate_tests(metafunc):
    """Override pytest's default test collection function.

    For each test in this directory which uses the `env_browser` fixture,
    the given test is called once for each value found in the
    `E2E_WEBDRIVER_BROWSERS` environment variable."""
    if 'env_browser' in metafunc.fixturenames:
        # In Python 2.7 the fallback kwarg of os.environ.get is `failobj`,
        # in 3.x it's `default`.
        browsers = os.environ.get('E2E_WEBDRIVER_BROWSERS',
                                  'Firefox').split()
        metafunc.parametrize('env_browser', browsers, indirect=True)


@pytest.fixture()
def env_browser(request):
    """Fixture for a webdriver instance of the browser."""
    if request.param is None:
        request.param = "Firefox"

    # Create instance of webdriver.`request.param`()
    browser = getattr(webdriver, request.param)()
    # Add finalizer to quit the webdriver instance
    request.addfinalizer(lambda: browser.quit())
    return browser
