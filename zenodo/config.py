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

SUPPORT_EMAIL = "info@zenodo.org"

# DataCite
# ========
ZENODO_LOCAL_DOI_PREFIXES = ["10.5072", "10.5281"]
DATACITE_DOI_PREFIX = "10.5072"

# Debug
# =====
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Language
# ========
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = []

# Celery
# ======
BROKER_URL = "amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

# Cache
# =========
CACHE_KEY_PREFIX = "cache::"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"

# Deposit
# =======
DEPOSIT_CONTRIBUTOR_TYPES = [
    dict(label='Contact person', marc='prc', datacite='ContactPerson'),
    dict(label='Data collector', marc='col', datacite='DataCollector'),
    dict(label='Data curator', marc='cur', datacite='DataCurator'),
    dict(label='Data manager', marc='dtm', datacite='DataManager'),
    dict(label='Editor', marc='edt', datacite='Editor'),
    dict(label='Researcher', marc='res', datacite='Researcher'),
    dict(label='Rights holder', marc='cph', datacite='RightsHolder'),
    dict(label='Sponsor', marc='spn', datacite='Sponsor'),
    dict(label='Other', marc='oth', datacite='Other'),
]

# ElasticSearch
# =========
ELASTICSEARCH_HOST = "localhost"

# Frontpage
# =========
FRONTPAGE_ENDPOINT = "zenodo_frontpage.index"

# OAuthclient
OAUTHCLIENT_REMOTE_APPS = dict(
    # github=dict(
    #     title='GitHub',
    #     description='Software collaboration platform, with one-click '
    #                 'software preservation in Zenodo.',
    #     icon='fa fa-github',
    #     authorized_handler="zenodo.modules.github.views.handlers:authorized",
    #     disconnect_handler="zenodo.modules.github.views.handlers:disconnect",
    #     signup_handler=dict(
    #         info="zenodo.modules.github.views.handlers:account_info",
    #         setup="zenodo.modules.github.views.handlers:account_setup",
    #         view="invenio.modules.oauthclient.handlers:signup_handler",
    #     ),
    #     params=dict(
    #         request_token_params={
    #             'scope': 'user:email,admin:repo_hook,read:org'
    #         },
    #         base_url='https://api.github.com/',
    #         request_token_url=None,
    #         access_token_url="https://github.com/login/oauth/access_token",
    #         access_token_method='POST',
    #         authorize_url="https://github.com/login/oauth/authorize",
    #         app_key="OAUTHCLIENT_GITHUB_CREDENTIALS",
    #     )
    # ),
    orcid=dict(
        title='ORCID',
        description='Connecting Research and Researchers.',
        icon='',
        authorized_handler="invenio_oauthclient.handlers"
                           ":authorized_signup_handler",
        disconnect_handler="invenio_oauthclient.handlers"
                           ":disconnect_handler",
        signup_handler=dict(
            info="invenio_oauthclient.contrib.orcid:account_info",
            setup="invenio_oauthclient.contrib.orcid:account_setup",
            view="invenio_oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={'scope': '/authenticate'},
            base_url='https://pub.orcid.org/',
            request_token_url=None,
            access_token_url="https://pub.orcid.org/oauth/token",
            access_token_method='POST',
            authorize_url="https://orcid.org/oauth/authorize?show_login=true",
            app_key="OAUTHCLIENT_ORCID_CREDENTIALS",
            content_type="application/json",
        )
    ),
)

OAUTHCLIENT_GITHUB_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

OAUTHCLIENT_ORCID_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

# DO NOT COMMIT
OAUTHCLIENT_ORCID_CREDENTIALS = dict(
    consumer_key='0000-0001-8135-3489',
    consumer_secret='527810db-6b4e-46a3-9c56-f8667d32e38a',
)

# OpenAIRE
# ========
OPENAIRE_SCHEMAS_HOST = 'zenodo.org'
OPENAIRE_JSONRESOLVER_GRANTS_HOST = 'zenodo.org'

# Pages
# =====
PAGES_WHITELIST_CONFIG_KEYS = [
    'DATACITE_DOI_PREFIX',
    'DEPOSIT_CONTRIBUTOR_TYPES',
    'FRONTPAGE_ENDPOINT',
    'SUPPORT_EMAIL',
    'THEME_SITENAME',
]

# Records
# =======
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
    ),
)

RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='zenodo_record_minter',
        pid_fetcher='zenodo_record_fetcher',
        list_route='/records/',
        item_route='/records/<pid_value>',
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': ('zenodo.modules.records.serializers'
                                 ':record_to_json_serializer'),
        },
        search_serializers={
            'application/json': ('zenodo.modules.records.serializers'
                                 ':search_to_json_serializer'),
        },
    ),
)

# Accounts
# ========
RECAPTCHA_PUBLIC_KEY = "CHANGE_ME"
RECAPTCHA_SECRET_KEY = "CHANGE_ME"

SECURITY_REGISTER_USER_TEMPLATE = \
    "zenodo_theme/security/register_user.html"
SECURITY_LOGIN_USER_TEMPLATE = \
    "zenodo_theme/security/login_user.html"

SECURITY_CONFIRM_SALT = "CHANGE_ME"
SECURITY_EMAIL_SENDER = SUPPORT_EMAIL
SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to Zenodo!")
SECURITY_LOGIN_SALT = "CHANGE_ME"
SECURITY_PASSWORD_SALT = "CHANGE_ME"
SECURITY_REMEMBER_SALT = "CHANGE_ME"
SECURITY_RESET_SALT = "CHANGE_ME"

# Theme
# =====
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
# ======
SEARCH_AUTOINDEX = []
SEARCH_UI_SEARCH_API = "invenio_records_rest.recid_list"
SEARCH_UI_SEARCH_TEMPLATE = "zenodo_search_ui/search.html"
SEARCH_DOC_TYPE_DEFAULT = None


# Database
# ========
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://localhost/zenodo")
SQLALCHEMY_ECHO = False
