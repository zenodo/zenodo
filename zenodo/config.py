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

"""Zenodo default application configuration."""

from __future__ import absolute_import, print_function

import os


def _(x):
    """Identity function for string extraction."""
    return x

# Database
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://localhost/zenodo")
SQLALCHEMY_ECHO = False

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = []

# Distributed task queue
BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

# Cache
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"

# ElasticSearch
ELASTICSEARCH_HOST = "localhost"

# Accounts
RECAPTCHA_PUBLIC_KEY = "CHANGE_ME"
RECAPTCHA_SECRET_KEY = "CHANGE_ME"

SECURITY_REGISTER_USER_TEMPLATE = \
    "zenodo_theme/security/register_user.html"
SECURITY_LOGIN_USER_TEMPLATE = \
    "zenodo_theme/security/login_user.html"

SECURITY_CONFIRM_SALT = "CHANGE_ME"
SECURITY_EMAIL_SENDER = "info@zenodo.org"
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to Zenodo!")
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SALT = "CHANGE_ME"
SECURITY_REMEMBER_SALT = "CHANGE_ME"
SECURITY_RESET_SALT = "CHANGE_ME"

# Theme
THEME_SITENAME = _("Zenodo")
THEME_TWITTERHANDLE = "@zenodo_org"
THEME_LOGO = "img/zenodo.svg"
THEME_GOOGLE_SITE_VERIFICATION = [
    "5fPGCLllnWrvFxH9QWI0l1TadV7byeEvfPcyK2VkS_s",
    "Rp5zp04IKW-s1IbpTOGB7Z6XY60oloZD5C3kTM-AiY4"
]

BASE_TEMPLATE = "zenodo_theme/page.html"
COVER_TEMPLATE = "zenodo_theme/page_cover.html"
SETTINGS_TEMPLATE = "invenio_theme/page_settings.html"

# Search
SEARCH_AUTOINDEX = []

# Records configuration
ZENODO_LEGACY_FORMATS = {
    'dcite': 'application/x-datacite+xml',
    'dcite3': 'application/x-datacite+xml',
    'hm': 'application/marcxml+xml',
    'hx': 'application/x-bibtex',
    'xd': 'application/xml',
    'xe': None,
    'xm': 'application/marcxml+xml',
    'xn': None,
    'xw': None,
    'json': 'application/json',
}

RECORDS_UI_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        route='/record/<pid_value>',
        template='zenodo_records/record_detail.html',
    ),
    record_export=dict(
        pid_type='recid',
        route='/record/<pid_value>/export/<any({0}):format>'.format(", ".join(
            list(ZENODO_LEGACY_FORMATS.keys()))),
        template='zenodo_records/record_export.html',
    ), )
RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='recid_minter',
        list_route='/records/',
        item_route='/records/<pid_value>',
    ), )

# DebugToolbar
DEBUG_TB_INTERCEPT_REDIRECTS = False

# DataCite DOI minting:
ZENODO_LOCAL_DOI_PREFIXES = ["10.5072", "10.5281"]

DATACITE_DOI_PREFIX = "10.5072"
