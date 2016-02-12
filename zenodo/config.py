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

from invenio_openaire.config import OPENAIRE_REST_ENDPOINTS
from invenio_records_rest.facets import terms_filter


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
RECORDS_UI_TOMBSTONE_TEMPLATE = "zenodo_records/tombstone.html"

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
            'application/json': (
                'zenodo.modules.records.serializers.json_v1_response'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_response'),
            # 'application/x-datacite+xml': (
            #     'zenodo.modules.records.serializers.datacite_v1_response'),
            # 'application/x-bibtex': (
            #     'zenodo.modules.records.serializers.bibtex_v1_response'),
        },
        search_serializers={
            'application/json': (
                'zenodo.modules.records.serializers:json_v1_search'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_search'),
        },
        default_media_type='application/json',
    ),
)
# Default OpenAIRE API endpoints.
RECORDS_REST_ENDPOINTS.update(OPENAIRE_REST_ENDPOINTS)

RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        best_match=dict(
            fields=['-_score'],
            title='Best match',
            default_order='asc',
            order=1,
        ),
        most_recent=dict(
            fields=['-creation_date'],
            title='Most recent',
            default_order='asc',
            order=2,
        ),
        publication_date=dict(
            fields=['publication_date'],
            title='Publication date',
            default_order='desc',
            order=3,
        ),
        title=dict(
            fields=['title', ],
            title='Title',
            order=4,
        ),
        # conference_session=dict(
        #     fields=['conference_part:asc', 'conference_contribution:desc'],
        #     title='Conference session',
        #     default_order='desc',
        #     order=4,
        # ),
        journal=dict(
            fields=[
                'journal.year',
                'journal.volume',
                'journal.issue',
                'journal.pages',
            ],
            title='Journal',
            default_order='desc',
            order=6,
        ),
    )
)

RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(
            type=dict(
                terms=dict(field="upload_type.type"),
                aggs=dict(
                    subtype=dict(
                        terms=dict(field="upload_type.subtype"),
                    )
                )
            ),
            access_right=dict(
                terms=dict(field="access_right"),
            ),
        ),
        filters=dict(
            communities=terms_filter('communities'),
        ),
        post_filters=dict(
            access_right=terms_filter('access_right'),
            type=terms_filter('upload_type.type'),
            subtype=terms_filter('upload_type.subtype'),
        )
    )
)

# Accounts
# ========
# DO NOT COMMIT
RECAPTCHA_PUBLIC_KEY = "6LdejRcTAAAAANuTnSJou_Iw2Rzpaaf0NEApmZYr"
RECAPTCHA_PRIVATE_KEY = "6LdejRcTAAAAAEA7LvsiEhDIc4jZdnRghAXY6JI-"

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

# Search
# ======
SEARCH_AUTOINDEX = []
SEARCH_UI_SEARCH_API = "/api/records/"
SEARCH_UI_SEARCH_TEMPLATE = "zenodo_search_ui/search.html"
SEARCH_DOC_TYPE_DEFAULT = None
SEARCH_ALLOWED_KEYWORDS = [
    'communities',
    'title',
    'authors.name',
    'access_right',
    'upload_type.type',
    'upload_type.subtype',
]

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
HEADER_TEMPLATE = "zenodo_theme/header.html"

REQUIREJS_CONFIG = "js/zenodo-build.js"

# User profile
# ============
USERPROFILES_EXTEND_SECURITY_FORMS = True

# Database
# ========
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://localhost/zenodo")
SQLALCHEMY_ECHO = False
