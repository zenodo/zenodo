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

"""Zenodo default application configuration."""

from __future__ import absolute_import, print_function

import copy
import os

from flask import request
from invenio_deposit.config import \
    DEPOSIT_REST_ENDPOINTS as INVENIO_DEPOSIT_REST_ENDPOINTS
from invenio_openaire.config import OPENAIRE_REST_DEFAULT_SORT, \
    OPENAIRE_REST_ENDPOINTS, OPENAIRE_REST_FACETS, \
    OPENAIRE_REST_SORT_OPTIONS
from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_records_rest.facets import terms_filter


def _(x):
    """Identity function for string extraction."""
    return x

#: Email address for support.
SUPPORT_EMAIL = "info@zenodo.org"

# DataCite
# ========
#: DOI prefixes considered as local prefixes.
ZENODO_LOCAL_DOI_PREFIXES = ["10.5072", "10.5281"]

#: The instance's DOI prefix.
DATACITE_DOI_PREFIX = "10.5072"


# Debug
# =====
#: Do not allow DebugToolbar to redirects redirects.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Language
# ========
#: Default language.
BABEL_DEFAULT_LANGUAGE = 'en'
#: Default timezone.
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
#: Other supported languages.
I18N_LANGUAGES = []

# Celery
# ======
#: Default broker (RabbitMQ on locahost).
BROKER_URL = "amqp://guest:guest@localhost:5672//"
#: Default Celery result backend.
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
#: Accepted content types for Celery.
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

# Cache
# =========
#: Cache key prefix
CACHE_KEY_PREFIX = "cache::"
#: URL of Redis db.
CACHE_REDIS_URL = "redis://localhost:6379/0"
#: Default cache type.
CACHE_TYPE = "redis"
#: Default cache URL for sessions.
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/2"

# Deposit
# =======
#: Template for deposit list view.
DEPOSIT_UI_INDEX_TEMPLATE = "zenodo_deposit/index.html"
#: Allow list of contributor types.
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
DEPOSIT_CONTRIBUTOR_MARC2DATACITE = {
    x['marc']: x['datacite'] for x in DEPOSIT_CONTRIBUTOR_TYPES
}
DEPOSIT_CONTRIBUTOR_DATACITE2MARC = {
    x['datacite']: x['marc'] for x in DEPOSIT_CONTRIBUTOR_TYPES
}

#: Default JSON Schema for deposit
DEPOSIT_DEFAULT_JSONSCHEMA = 'zenodo_deposit/deposit-v1.0.0.json'

#: Angular Schema Form for deposit
DEPOSIT_DEFAULT_SCHEMAFORM = 'json/zenodo_deposit/deposit_form.json'

#: Endpoints for deposit.
DEPOSIT_REST_ENDPOINTS = copy.deepcopy(INVENIO_DEPOSIT_REST_ENDPOINTS)
DEPOSIT_REST_ENDPOINTS['dep'].update(
    dict(
        record_loaders={
            'application/json': (
                'zenodo.modules.deposit.loaders:legacyjson_loader'),
            'application/vnd.zenodo.v1+json': lambda: request.get_json(),
        },
        record_serializers={
            'application/json': (
                'zenodo.modules.records.serializers:legacyjson_v1_response'),
            'application/vnd.zenodo.v1+json': (
                'invenio_records_rest.serializers:json_v1_response'),
        },
        search_serializers={
            'application/json': (
                'zenodo.modules.records.serializers:legacyjson_v1_search'),
            'application/vnd.zenodo.v1+json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
        list_route='/deposit/depositions/',
        item_route='/deposit/depositions/<pid_value>',
    ),
)

# Formatter
# =========
#: List of allowed titles in badges.
FORMATTER_BADGES_ALLOWED_TITLES = ['DOI', 'doi']

#: Mapping of titles.
FORMATTER_BADGES_TITLE_MAPPING = {'doi': 'DOI'}

# Frontpage
# =========
#: Frontpage endpoint.
FRONTPAGE_ENDPOINT = "zenodo_frontpage.index"


# Logging
# =======
#: Overwrite default Sentry extension class to support Sentry 6.
LOGGING_SENTRY_CLASS = 'invenio_logging.sentry6:Sentry6'


#: Defintion of OAuth client applications.
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

#: Credentials for GitHub (must be changed to work).
OAUTHCLIENT_GITHUB_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

#: Credentials for ORCID (must be changed to work).
OAUTHCLIENT_ORCID_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

# OpenAIRE
# ========
#: Hostname for JSON Schemas in OpenAIRE.
OPENAIRE_SCHEMAS_HOST = 'zenodo.org'
#: Hostname for OpenAIRE's grant resolver.
OPENAIRE_JSONRESOLVER_GRANTS_HOST = 'dx.zenodo.org'

# OpenDefinition
# ==============
#: Hostname for JSON Schemas in OpenAIRE.
OPENDEFINITION_SCHEMAS_HOST = 'zenodo.org'
#: Hostname for OpenAIRE's grant resolver.
OPENDEFINITION_JSONRESOLVER_HOST = 'dx.zenodo.org'

# JSON Schemas
# ============
#: Hostname for JSON Schemas.
JSONSCHEMAS_HOST = 'zenodo.org'

# Pages
# =====
#: Allowed configuration variables to use in page templates.
PAGES_WHITELIST_CONFIG_KEYS = [
    'DATACITE_DOI_PREFIX',
    'DEPOSIT_CONTRIBUTOR_TYPES',
    'FRONTPAGE_ENDPOINT',
    'SUPPORT_EMAIL',
    'THEME_SITENAME',
]
PAGES_TEMPLATES = [
    ('invenio_pages/default.html', 'Default'),
    ('invenio_pages/dynamic.html', 'Default dynamic'),
    ('zenodo_theme/full_page.html', 'Default full page'),
]

# Records
# =======
#: Mapping of old export formats to new content type.
ZENODO_RECORDS_EXPORTFORMATS = {
    'dcite': dict(
        title='DataCite XML',
        serializer='zenodo.modules.records.serializers.datacite_v31',
    ),
    'dcite3': dict(
        title='DataCite XML',
        serializer='zenodo.modules.records.serializers.datacite_v31',
        order=3,
    ),
    'hm': dict(
        title='MARC21 XML',
        serializer='zenodo.modules.records.serializers.marcxml_v1',
    ),
    'hx': dict(
        title='BibTeX',
        serializer='zenodo.modules.records.serializers.bibtex_v1',
        order=2,
    ),
    'xd': dict(
        title='Dublin Core',
        serializer='zenodo.modules.records.serializers.dc_v1',
        order=4,
    ),
    'xm': dict(
        title='MARC21 XML',
        serializer='zenodo.modules.records.serializers.marcxml_v1',
        order=5,
    ),
    'json': dict(
        title='JSON',
        serializer='zenodo.modules.records.serializers.json_v1',
        order=1,
    ),
    # Unsupported formats.
    'xe': None,
    'xn': None,
    'xw': None,
}

#: Endpoints for displaying records.
RECORDS_UI_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        route='/record/<pid_value>',
        template='zenodo_records/record_detail.html',
    ),
    record_export=dict(
        pid_type='recid',
        route='/record/<pid_value>/export/<any({0}):format>'.format(", ".join(
            list(ZENODO_RECORDS_EXPORTFORMATS.keys()))),
        template='zenodo_records/record_export.html',
        view_imp='zenodo.modules.records.views.records_ui_export',
    ),
    record_preview=dict(
        pid_type='recid',
        route='/record/<pid_value>/preview/<filename>',
        view_imp='invenio_previewer.views.preview',
    ),
    record_files=dict(
        pid_type='recid',
        route='/record/<pid_value>/files/<filename>',
        view_imp='invenio_files_rest.views.file_download_ui',
    ),
)
#: Default tombstone template.
RECORDS_UI_TOMBSTONE_TEMPLATE = "zenodo_records/tombstone.html"

#: Files REST permission factory
FILES_REST_PERMISSION_FACTORY = \
    'zenodo.modules.records.permissions:FilePermission'

#: Records REST API endpoints.
RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='zenodo_record_minter',
        pid_fetcher='zenodo_record_fetcher',
        list_route='/records/',
        item_route='/records/<pid_value>',
        search_index='records',
        search_type=['record-v1.0.0'],
        search_factory_imp='invenio_records_rest.query.es_search_factory',
        record_serializers={
            'application/json': (
                'zenodo.modules.records.serializers.json_v1_response'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_response'),
            'application/x-bibtex': (
                'zenodo.modules.records.serializers.bibtex_v1_response'),
            'application/x-datacite+xml': (
                'zenodo.modules.records.serializers.datacite_v31_response'),
            'application/x-dc+xml': (
                'zenodo.modules.records.serializers.dc_v1_response'),
        },
        search_serializers={
            'application/json': (
                'zenodo.modules.records.serializers:json_v1_search'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_search'),
            'application/x-bibtex': (
                'zenodo.modules.records.serializers:bibtex_v1_search'),
            'application/x-datacite+xml': (
                'zenodo.modules.records.serializers.datacite_v31_search'),
            'application/x-dc+xml': (
                'zenodo.modules.records.serializers.dc_v1_search'),
        },
        default_media_type='application/json',
    ),
)
# Default OpenAIRE API endpoints.
RECORDS_REST_ENDPOINTS.update(OPENAIRE_REST_ENDPOINTS)
RECORDS_REST_ENDPOINTS.update(OPENDEFINITION_REST_ENDPOINTS)

#: Sort options records REST API.
RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            fields=['-_score'],
            title='Best match',
            default_order='asc',
            order=1,
        ),
        mostrecent=dict(
            fields=['-_created'],
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
        conference_session=dict(
            fields=['meetings.session:asc', 'meetings.session_part:desc'],
            title='Conference session',
            default_order='desc',
            order=4,
        ),
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
RECORDS_REST_SORT_OPTIONS.update(OPENAIRE_REST_SORT_OPTIONS)

#: Default sort for records REST API.
RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(query='bestmatch', noquery='mostrecent'),
)
RECORDS_REST_DEFAULT_SORT.update(OPENAIRE_REST_DEFAULT_SORT)

#: Defined facets for records REST API.
RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(
            type=dict(
                terms=dict(field="resource_type.type"),
                aggs=dict(
                    subtype=dict(
                        terms=dict(field="resource_type.subtype"),
                    )
                )
            ),
            access_right=dict(
                terms=dict(field="access_right"),
            ),
            file_type=dict(
                terms=dict(field="files.type"),
            ),
            keywords=dict(
                terms=dict(field="keywords"),
            ),
        ),
        filters=dict(
            communities=terms_filter('communities'),
            provisional_communities=terms_filter('provisional_communities'),
        ),
        post_filters=dict(
            access_right=terms_filter('access_right'),
            type=terms_filter('resource_type.type'),
            subtype=terms_filter('resource_type.subtype'),
            file_type=terms_filter('files.type'),
            keywords=terms_filter('keywords'),
        )
    )
)
RECORDS_REST_FACETS.update(OPENAIRE_REST_FACETS)

# Previewer
# =========
#: Base CSS bundle to include in all previewers
PREVIEWER_BASE_CSS_BUNDLES = ['zenodo_theme_css']
"""Basic bundle which includes Font-Awesome/Bootstrap."""
#: Base JS bundle to include in all previewers
PREVIEWER_BASE_JS_BUNDLES = ['zenodo_theme_js']
"""Basic bundle which includes Bootstrap/jQuery."""


# OAI-PMH
# =======
#: Index to use for the OAI-PMH server.
OAISERVER_RECORD_INDEX = 'records'
#: OAI identifier prefix
OAISERVER_ID_PREFIX = 'oai:zenodo.org:recid/'
#: Number of records to return per page in OAI-PMH results.
OAISERVER_PAGE_SIZE = 25
#: Support email for OAI-PMH.
OAISERVER_ADMIN_EMAILS = [SUPPORT_EMAIL]
#: Do not register signals to automatically update record on updates.
OAISERVER_REGISTER_RECORD_SIGNALS = False
#: Metadata formats for OAI-PMH server
OAISERVER_METADATA_FORMATS = {
    'marcxml': {
        'namespace': 'http://www.loc.gov/MARC21/slim',
        'schema': 'http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_marc21_v1',
    },
    'marc21': {
        'namespace': 'http://www.loc.gov/MARC21/slim',
        'schema': 'http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_marc21_v1',
    },
    'datacite3': {
        'namespace': 'http://datacite.org/schema/kernel-3',
        'schema': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_datacite_v31',
    },
    'oai_datacite': {
        'namespace': 'http://datacite.org/schema/kernel-3',
        'schema': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_oai_datacite',
    },
    'oai_dc': {
        'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_oai_dc',
    }
}

# Migrator
# ========
# MIGRATOR_RECORDS_POST_TASK = 'zenodo_migrationkit.tasks.migrate_record'

# REST
# ====
#: Enable CORS support.
REST_ENABLE_CORS = True

# Accounts
# ========
#: Recaptcha public key (change to enable).
RECAPTCHA_PUBLIC_KEY = None
#: Recaptcha private key (change to enable).
RECAPTCHA_PRIVATE_KEY = None

#: User registration template.
SECURITY_REGISTER_USER_TEMPLATE = \
    "zenodo_theme/security/register_user.html"
#: Login registration template.
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
#: Default API endpoint for search UI.
SEARCH_UI_SEARCH_API = "/api/records/"
#: Default template for search UI.
SEARCH_UI_SEARCH_TEMPLATE = "zenodo_search_ui/search.html"
#: Angular template for rendering search results.
SEARCH_UI_JSTEMPLATE_RESULTS = "templates/zenodo_search_ui/results.html"
#: Angular template for rendering search facets.
SEARCH_UI_JSTEMPLATE_FACETS = "templates/zenodo_search_ui/facets.html"
#: Default Elasticsearch document type.
SEARCH_DOC_TYPE_DEFAULT = None
#: Do not map any keywords.
SEARCH_ELASTIC_KEYWORD_MAPPING = {}

# Communities
# ===========
#: Override templates to use custom search-js
COMMUNITIES_COMMUNITY_TEMPLATE = "zenodo_theme/communities/base.html"
#: Override templates to use custom search-js
COMMUNITIES_CURATE_TEMPLATE = "zenodo_theme/communities/curate.html"
#: Override templates to use custom search-js
COMMUNITIES_SEARCH_TEMPLATE = "zenodo_theme/communities/search.html"

#: Angular template for rendering search results for curation.
COMMUNITIES_JSTEMPLATE_RESULTS_CURATE = \
    "templates/zenodo_search_ui/results_curate.html"
#: Email sender for communities emails.
COMMUNITIES_REQUEST_EMAIL_SENDER = SUPPORT_EMAIL

# Theme
# =====
#: Default site name.
THEME_SITENAME = _("Zenodo")
#: Default site URL (used only when not in a context - e.g. like celery tasks).
THEME_SITEURL = "https://zenodo.org"
#: Endpoint for breadcrumb root.
THEME_BREADCRUMB_ROOT_ENDPOINT = 'zenodo_frontpage.index'
#: Twitter handle.
THEME_TWITTERHANDLE = "@zenodo_org"
#: Path to logo file.
THEME_LOGO = "img/zenodo.svg"
#: Google Site Verification ids.
THEME_GOOGLE_SITE_VERIFICATION = [
    "5fPGCLllnWrvFxH9QWI0l1TadV7byeEvfPcyK2VkS_s",
    "Rp5zp04IKW-s1IbpTOGB7Z6XY60oloZD5C3kTM-AiY4"
]
#: Piwik site id.
THEME_PIWIK_ID = None

THEME_MATHJAX_CDN = \
    '//cdn.mathjax.org/mathjax/latest/MathJax.js' \
    '?config=TeX-AMS-MML_HTMLorMML'

#: Base template for entire site.
BASE_TEMPLATE = "zenodo_theme/page.html"
#: Cover template for entire site.
COVER_TEMPLATE = "zenodo_theme/page_cover.html"
#: Settings template for entire site.
SETTINGS_TEMPLATE = "invenio_theme/page_settings.html"
#: Header template for entire site.
HEADER_TEMPLATE = "zenodo_theme/header.html"
#: JavaScript file containing the require.js build configuration.
REQUIREJS_CONFIG = "js/zenodo-build.js"

# User profile
# ============
#: Extend account registration form with user profiles fields.
USERPROFILES_EXTEND_SECURITY_FORMS = True

# Database
# ========
#: Default database host.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://localhost/zenodo")
#: Do not print SQL queries to console.
SQLALCHEMY_ECHO = False
#: Track modifications to objects.
SQLALCHEMY_TRACK_MODIFICATIONS = True
