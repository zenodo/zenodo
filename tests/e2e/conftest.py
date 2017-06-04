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
from elasticsearch.exceptions import RequestError
from invenio_db import db as db_
from invenio_search import current_search, current_search_client
from selenium import webdriver
from sqlalchemy_utils.functions import create_database, database_exists
from invenio_accounts.testutils import create_test_user
from invenio_admin.permissions import action_admin_access
from invenio_access.models import ActionUsers
from invenio_deposit.permissions import \
        action_admin_access as deposit_admin_access
from zenodo.factory import create_app


@pytest.yield_fixture(scope='session')
def app():
    """Flask application fixture."""
    _app = create_app(
        # CELERY_ALWAYS_EAGER=True,
        # CELERY_CACHE_BACKEND="memory",
        # CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        # CELERY_RESULT_BACKEND="cache",
        DEBUG_TB_ENABLED=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME",
        MAIL_SUPPRESS_SEND=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )

    with _app.app_context():
        yield _app


@pytest.yield_fixture()
def es(app):
    """Provide elasticsearch access."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete())
        list(current_search.create())
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture()
def db(app):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


def pytest_generate_tests(metafunc):
    """Override pytest's default test collection function.

    For each test in this directory which uses the `env_browser` fixture,
    the given test is called once for each value found in the
    `E2E_WEBDRIVER_BROWSERS` environment variable.
    """
    if 'env_browser' in metafunc.fixturenames:
        # In Python 2.7 the fallback kwarg of os.environ.get is `failobj`,
        # in 3.x it's `default`.
        browsers = os.environ.get('E2E_WEBDRIVER_BROWSERS',
                                  'Firefox').split()
        metafunc.parametrize('env_browser', browsers, indirect=True)


@pytest.yield_fixture()
def env_browser(request):
    """Fixture for a webdriver instance of the browser."""
    if request.param is None:
        request.param = "Firefox"

    # Create instance of webdriver.`request.param`()
    browser = getattr(webdriver, request.param)()

    yield browser

    # Quit the webdriver instance
    browser.quit()

@pytest.fixture()
def users(db):
    """Create users."""
    user1 = create_test_user(email='info@zenodo.org', password='tester')
    user2 = create_test_user(email='test@zenodo.org', password='tester2')
    user_admin = create_test_user(email='admin@zenodo.org',
                                  password='admin')

    with db.session.begin_nested():
        # set admin permissions
        db.session.add(ActionUsers(action=action_admin_access.value,
                                   user=user_admin))
        db.session.add(ActionUsers(action=deposit_admin_access.value,
                                   user=user_admin))
    db.session.commit()

    return [
        {'email': user1.email, 'id': user1.id},
        {'email': user2.email, 'id': user2.id},
        {'email': user_admin.email, 'id': user_admin.id}
    ]
