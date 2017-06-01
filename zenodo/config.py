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

"""Zenodo default application configuration.

You can customize these configuration variables on your instance by either
setting environment variables prefixed with ``APP_``, e.g.

.. code-block:: console

   export APP_SUPPORT_EMAIL=info@example.org

or provide an instance configuration file (Python syntax):

.. code-block:: python

    # ${VIRTUAL_ENV}/var/instance/zenodo.cfg
    SUPPORT_EMAIL = "info@example.org"

Configuration variables
~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function

import os
from datetime import timedelta

from celery.schedules import crontab
from invenio_deposit.config import DEPOSIT_REST_DEFAULT_SORT, \
    DEPOSIT_REST_FACETS, DEPOSIT_REST_SORT_OPTIONS
from invenio_deposit.scopes import write_scope
from invenio_deposit.utils import check_oauth2_scope
from invenio_github.config import GITHUB_REMOTE_APP
from invenio_oauthclient.contrib.orcid import REMOTE_APP as ORCID_REMOTE_APP
from invenio_openaire.config import OPENAIRE_REST_DEFAULT_SORT, \
    OPENAIRE_REST_ENDPOINTS, OPENAIRE_REST_FACETS, \
    OPENAIRE_REST_SORT_OPTIONS
from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_pidrelations.config import RelationType
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all
from zenodo_accessrequests.config import ACCESSREQUESTS_RECORDS_UI_ENDPOINTS

from zenodo.modules.records.permissions import deposit_delete_permission_factory, \
    deposit_read_permission_factory, deposit_update_permission_factory, \
    record_create_permission_factory, record_update_permission_factory


def _(x):
    """Identity function for string extraction."""
    return x

#: Email address for support.
SUPPORT_EMAIL = "info@zenodo.org"
MAIL_SUPPRESS_SEND = True

# DataCite
# ========
#: DOI prefixes considered as local prefixes.
ZENODO_LOCAL_DOI_PREFIXES = ["10.5072", "10.5281"]

#: DataCite API - URL endpoint.
PIDSTORE_DATACITE_URL = "https://mds.datacite.org"
#: DataCite API - Disable test mode (we however use the test prefix).
PIDSTORE_DATACITE_TESTMODE = False
#: DataCite API - Prefix for minting DOIs in (10.5072 is a test prefix).
PIDSTORE_DATACITE_DOI_PREFIX = "10.5072"
#: DataCite MDS username.
PIDSTORE_DATACITE_USERNAME = "CERN.ZENODO"
#: DataCite MDS password.
PIDSTORE_DATACITE_PASSWORD = "CHANGE_ME"

#: Zenodo PID relations
PIDRELATIONS_RELATION_TYPES = [
    RelationType(0, 'version', 'Version',
                 'invenio_pidrelations.contrib.versioning:PIDVersioning',
                 'zenodo.modules.records.serializers.schemas.pidrelations:'
                 'VersionRelation'),
    RelationType(1, 'record_draft', 'Record Draft',
                 'invenio_pidrelations.contrib.records:RecordDraft',
                 None),
]

#: Enable the DataCite minding of DOIs after Deposit publishing
DEPOSIT_DATACITE_MINTING_ENABLED = False

# Debug
# =====
#: Do not allow DebugToolbar to redirects redirects.
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Assets
# ======
#: Switch of assets debug.
ASSETS_DEBUG = False
#: Switch of automatic building.
ASSETS_AUTO_BUILD = False
#: Remove app.static_folder from source list of static folders.
COLLECT_FILTER = 'zenodo.modules.theme.collect:collect_staticroot_removal'

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
#: Beat schedule
CELERYBEAT_SCHEDULE = {
    'embargo-updater': {
        'task': 'zenodo.modules.records.tasks.update_expired_embargos',
        'schedule': crontab(minute=2, hour=0),
    },
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
    },
    'openaire-updater': {
        'task': 'zenodo.modules.utils.tasks.update_search_pattern_sets',
        'schedule': timedelta(hours=2),
    },
}

# Cache
# =========
#: Cache key prefix
CACHE_KEY_PREFIX = "cache::"
#: Host
CACHE_REDIS_HOST = "localhost"
#: Port
CACHE_REDIS_PORT = 6379
#: DB
CACHE_REDIS_DB = 0
#: URL of Redis db.
CACHE_REDIS_URL = "redis://{0}:{1}/{2}".format(
    CACHE_REDIS_HOST, CACHE_REDIS_PORT, CACHE_REDIS_DB)
#: Default cache type.
CACHE_TYPE = "redis"
#: Default cache URL for sessions.
ACCOUNTS_SESSION_REDIS_URL = "redis://localhost:6379/2"
#: Cache for storing access restrictions
ACCESS_CACHE = 'zenodo.modules.cache:current_cache'

# CSL Citation Formatter
# ======================
#: Styles Endpoint for CSL
CSL_STYLES_API_ENDPOINT = '/api/csl/styles'
#: Records Endpoint for CSL
CSL_RECORDS_API_ENDPOINT = '/api/records/'
#: Template dirrectory for CSL
CSL_JSTEMPLATE_DIR = 'node_modules/invenio-csl-js/dist/templates/'
#: Template for CSL citation result
CSL_JSTEMPLATE_CITEPROC = 'templates/invenio_csl/citeproc.html'
#: Template for CSL citation list item
CSL_JSTEMPLATE_LIST_ITEM = 'templates/invenio_csl/item.html'
#: Template for CSL error
CSL_JSTEMPLATE_ERROR = os.path.join(CSL_JSTEMPLATE_DIR, 'error.html')
#: Template for CSL loading
CSL_JSTEMPLATE_LOADING = os.path.join(CSL_JSTEMPLATE_DIR, 'loading.html')
#: Template for CSL typeahead
CSL_JSTEMPLATE_TYPEAHEAD = os.path.join(CSL_JSTEMPLATE_DIR, 'typeahead.html')

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
#: Celery sentry logging
LOGGING_SENTRY_CELERY = True

# GitHub
# ======
#: Repositories list template.
GITHUB_TEMPLATE_INDEX = 'zenodo_github/settings/index.html'
#: Repository detail view template.
GITHUB_TEMPLATE_VIEW = 'zenodo_github/settings/view.html'
#: Record serializer to use for serialize record metadata
GITHUB_RECORD_SERIALIZER = 'zenodo.modules.records.serializers.githubjson_v1'
#: Time period after which a GitHub account sync should be initiated.
GITHUB_REFRESH_TIMEDELTA = timedelta(hours=3)
#: GitHub webhook url override
GITHUB_WEBHOOK_RECEIVER_URL = \
    'http://localhost:5000' \
    '/api/hooks/receivers/github/events/?access_token={token}'
#: Set Zenodo deposit class
GITHUB_RELEASE_CLASS = 'zenodo.modules.github.api:ZenodoGitHubRelease'
#: Set Zenodo deposit class
GITHUB_DEPOSIT_CLASS = 'zenodo.modules.deposit.api:ZenodoDeposit'
#: GitHub PID fetcher
GITHUB_PID_FETCHER = 'zenodo_doi_fetcher'
#: GitHub metdata file
GITHUB_METADATA_FILE = '.zenodo.json'
#: SIPStore
SIPSTORE_GITHUB_AGENT_JSONSCHEMA = 'sipstore/agent-githubclient-v1.0.0.json'
#: Set OAuth client application config.
GITHUB_REMOTE_APP.update(dict(
    description='Software collaboration platform, with one-click '
                'software preservation in Zenodo.',
))
GITHUB_REMOTE_APP['params']['request_token_params']['scope'] = \
    'user:email,admin:repo_hook,read:org'


#: Defintion of OAuth client applications.
OAUTHCLIENT_REMOTE_APPS = dict(
    github=GITHUB_REMOTE_APP,
    orcid=ORCID_REMOTE_APP,
)

#: Change default template for oauth sign up.
OAUTHCLIENT_SIGNUP_TEMPLATE = 'zenodo_theme/security/oauth_register_user.html'
#: Stop oauthclient from taking over template.
OAUTHCLIENT_TEMPLATE_KEY = None

#: Credentials for GitHub (must be changed to work).
GITHUB_APP_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

#: Credentials for ORCID (must be changed to work).
ORCID_APP_CREDENTIALS = dict(
    consumer_key="CHANGE_ME",
    consumer_secret="CHANGE_ME",
)

# OpenAIRE
# ========
#: Hostname for JSON Schemas in OpenAIRE.
OPENAIRE_SCHEMAS_HOST = 'zenodo.org'
#: Hostname for OpenAIRE's grant resolver.
OPENAIRE_JSONRESOLVER_GRANTS_HOST = 'dx.zenodo.org'
#: OpenAIRE data source IDs for Zenodo.
OPENAIRE_ZENODO_IDS = {
    'publication': 'opendoar____::2659',
    'dataset': 're3data_____::r3d100010468',
}
#: OpenAIRE ID namespace prefixes for Zenodo.
OPENAIRE_NAMESPACE_PREFIXES = {
    'publication': 'od______2659',
    'dataset': 'r37b0ad08687',
}
#: OpenAIRE API endpoint.
OPENAIRE_API_URL = 'http://dev.openaire.research-infrastructures.eu/is/mvc'
#: URL to OpenAIRE portal.
OPENAIRE_PORTAL_URL = 'https://beta.openaire.eu'

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
    'PIDSTORE_DATACITE_DOI_PREFIX',
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

# Deposit
# =======
#: PID minter used during record creation.
DEPOSIT_PID_MINTER = 'zenodo_record_minter'

_PID = 'pid(depid,record_class="zenodo.modules.deposit.api:ZenodoDeposit")'
#: Template for deposit list view.
DEPOSIT_SEARCH_API = '/api/deposit/depositions'
#: Mimetype for deposit search.
DEPOSIT_SEARCH_MIMETYPE = 'application/vnd.zenodo.v1+json'
#: Template for deposit list view.
DEPOSIT_UI_INDEX_TEMPLATE = 'zenodo_deposit/index.html'
#: Template to use for UI.
DEPOSIT_UI_NEW_TEMPLATE = 'zenodo_deposit/edit.html'
#: Template for <invenio-records-form>
DEPOSIT_UI_JSTEMPLATE_FORM = 'templates/zenodo_deposit/form.html'
#: Template for <invenio-records-actions>
DEPOSIT_UI_JSTEMPLATE_ACTIONS = 'templates/zenodo_deposit/actions.html'
#: Template for <invenio-files-upload-zone>
DEPOSIT_UI_JSTEMPLATE_UPLOADZONE = 'templates/zenodo_deposit/upload.html'
#: Template for <invenio-files-list>
DEPOSIT_UI_JSTEMPLATE_FILESLIST = 'templates/zenodo_deposit/list.html'
#: Endpoint for deposit.
DEPOSIT_UI_ENDPOINT = '{scheme}://{host}/deposit/{pid_value}'
#: Template path for angular form elements.
DEPOSIT_FORM_TEMPLATES_BASE = 'templates/zenodo_deposit'
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
DEPOSIT_CONTRIBUTOR_TYPES_LABELS = {
    x['datacite']: x['label'] for x in DEPOSIT_CONTRIBUTOR_TYPES
}

#: Default JSON Schema for deposit.
DEPOSIT_DEFAULT_JSONSCHEMA = 'deposits/records/record-v1.0.0.json'

#: Angular Schema Form for deposit.
DEPOSIT_DEFAULT_SCHEMAFORM = 'json/zenodo_deposit/deposit_form.json'
#: JSON Schema for deposit Angular Schema Form.
DEPOSIT_FORM_JSONSCHEMA = 'deposits/records/legacyrecord.json'

#: Template for deposit records API.
DEPOSIT_RECORDS_API = '/api/deposit/depositions/{pid_value}'

#: Alerts shown when actions are completed on deposit.
DEPOSIT_UI_RESPONSE_MESSAGES = dict(
    self=dict(
        message="Saved successfully."
    ),
    delete=dict(
        message="Deleted succesfully."
    ),
    discard=dict(
        message="Changes discarded succesfully."
    ),
    publish=dict(
        message="Published succesfully."
    ),
)

#: REST API configuration.
DEPOSIT_REST_ENDPOINTS = dict(
    depid=dict(
        pid_type='depid',
        pid_minter='zenodo_deposit_minter',
        pid_fetcher='zenodo_deposit_fetcher',
        record_class='zenodo.modules.deposit.api:ZenodoDeposit',
        record_loaders={
            'application/json': (
                'zenodo.modules.deposit.loaders:legacyjson_v1'),
            # 'application/vnd.zenodo.v1+json': (
            #    'zenodo.modules.deposit.loaders:deposit_json_v1'),
        },
        record_serializers={
            'application/json': (
                'zenodo.modules.records.serializers'
                ':deposit_legacyjson_v1_response'),
            'application/vnd.zenodo.v1+json': (
                'zenodo.modules.records.serializers:deposit_json_v1_response'),
        },
        search_class='invenio_deposit.search:DepositSearch',
        search_factory_imp='zenodo.modules.deposit.query.search_factory',
        search_serializers={
            'application/json': (
                'zenodo.modules.records.serializers'
                ':deposit_legacyjson_v1_search'),
            'application/vnd.zenodo.v1+json': (
                'zenodo.modules.records.serializers:deposit_json_v1_search'),
        },
        files_serializers={
            'application/json': (
                'zenodo.modules.records.serializers'
                ':deposit_legacyjson_v1_files_response'),
        },
        list_route='/deposit/depositions',
        item_route='/deposit/depositions/<{0}:pid_value>'.format(_PID),
        file_list_route=(
            '/deposit/depositions/<{0}:pid_value>/files'.format(_PID)),
        file_item_route=(
            '/deposit/depositions/<{0}:pid_value>/files/<file_key:key>'.format(
                _PID)),
        default_media_type='application/json',
        links_factory_imp='zenodo.modules.deposit.links:links_factory',
        create_permission_factory_imp=check_oauth2_scope(
            lambda record: record_create_permission_factory(
                record=record).can(),
            write_scope.id),
        read_permission_factory_imp=deposit_read_permission_factory,
        update_permission_factory_imp=check_oauth2_scope(
            lambda record: deposit_update_permission_factory(
                record=record).can(),
            write_scope.id),
        delete_permission_factory_imp=check_oauth2_scope(
            lambda record: deposit_delete_permission_factory(
                record=record).can(),
            write_scope.id),
        max_result_window=10000,
    ),
)
#: Depoist UI endpoints
DEPOSIT_RECORDS_UI_ENDPOINTS = {
    'depid': {
        'pid_type': 'depid',
        'route': '/deposit/<pid_value>',
        'template': 'zenodo_deposit/edit.html',
        'record_class': 'zenodo.modules.deposit.api:ZenodoDeposit',
    },
}

#: Endpoint for uploading files.
DEPOSIT_FILES_API = u'/api/files'

#: Size after which files are chunked when uploaded
DEPOSIT_FILEUPLOAD_CHUNKSIZE = 15 * 1024 * 1024  # 15 MiB

#: Maximum upload file size via application/mulitpart-formdata
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MiB

# SIPStore
# ========
#: Default JSON schema for the SIP agent
SIPSTORE_DEFAULT_AGENT_JSONSCHEMA = 'sipstore/agent-webclient-v1.0.0.json'

#: Enable the agent JSON schema
SIPSTORE_AGENT_JSONSCHEMA_ENABLED = True

#: Max length of SIPFile.filepath
SIPSTORE_FILEPATH_MAX_LEN = 1000


# Records
# =======
#: Standard record removal reasons.
ZENODO_REMOVAL_REASONS = [
    ('', ''),
    ('spam', 'Spam record, removed by Zenodo staff.'),
    ('uploader', 'Record removed on request by uploader.'),
    ('takedown', 'Record removed on request by third-party.'),
]
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
    'csl': dict(
        title='Citation Style Language JSON',
        serializer='zenodo.modules.records.serializers.csl_v1',
        order=6,
    ),
    'cp': dict(
        title='Citation',
        serializer='zenodo.modules.records.serializers.citeproc_v1',
        order=7,
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
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
    recid_export=dict(
        pid_type='recid',
        route='/record/<pid_value>/export/<any({0}):format>'.format(", ".join(
            list(ZENODO_RECORDS_EXPORTFORMATS.keys()))),
        template='zenodo_records/record_export.html',
        view_imp='zenodo.modules.records.views.records_ui_export',
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
    recid_preview=dict(
        pid_type='recid',
        route='/record/<pid_value>/preview/<path:filename>',
        view_imp='invenio_previewer.views.preview',
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
    recid_files=dict(
        pid_type='recid',
        route='/record/<pid_value>/files/<path:filename>',
        view_imp='invenio_records_files.utils.file_download_ui',
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
)
RECORDS_UI_ENDPOINTS.update(ACCESSREQUESTS_RECORDS_UI_ENDPOINTS)

#: Endpoint for record ui.
RECORDS_UI_ENDPOINT = '{scheme}://{host}/record/{pid_value}'

#: Permission factory for records-ui and deposit-ui
RECORDS_UI_DEFAULT_PERMISSION_FACTORY = \
    "zenodo.modules.records.permissions:deposit_read_permission_factory"

#: Default tombstone template.
RECORDS_UI_TOMBSTONE_TEMPLATE = "zenodo_records/tombstone.html"

ZENODO_RECORDS_UI_LINKS_FORMAT = "https://zenodo.org/record/{recid}"

#: Files REST permission factory
FILES_REST_PERMISSION_FACTORY = \
    'zenodo.modules.records.permissions:files_permission_factory'

#: Max object key length
FILES_REST_OBJECT_KEY_MAX_LEN = 1000

#: Max URI length
FILES_REST_FILE_URI_MAX_LEN = 1000

#: Records REST API endpoints.
RECORDS_API = '/api/records/{pid_value}'
RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='zenodo_record_minter',
        pid_fetcher='zenodo_record_fetcher',
        list_route='/records/',
        item_route='/records/<{0}:pid_value>'.format(
            'pid(recid,record_class="zenodo.modules.records.api:ZenodoRecord")'
        ),
        search_index='records',
        record_class='zenodo.modules.records.api:ZenodoRecord',
        search_type=['record-v1.0.0'],
        search_factory_imp='zenodo.modules.records.query.search_factory',
        record_serializers={
            'application/json': (
                'zenodo.modules.records.serializers.legacyjson_v1_response'),
            'application/vnd.zenodo.v1+json': (
                'zenodo.modules.records.serializers.json_v1_response'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_response'),
            'application/x-bibtex': (
                'zenodo.modules.records.serializers.bibtex_v1_response'),
            'application/x-datacite+xml': (
                'zenodo.modules.records.serializers.datacite_v31_response'),
            'application/x-dc+xml': (
                'zenodo.modules.records.serializers.dc_v1_response'),
            'application/vnd.citationstyles.csl+json': (
                'zenodo.modules.records.serializers.csl_v1_response'),
            'text/x-bibliography': (
                'zenodo.modules.records.serializers.citeproc_v1_response'),
        },
        search_serializers={
            'application/json': (
                'zenodo.modules.records.serializers:legacyjson_v1_search'),
            'application/vnd.zenodo.v1+json': (
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
        default_media_type='application/vnd.zenodo.v1+json',
        read_permission_factory_imp=allow_all,
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
            fields=['meeting.session', '-meeting.session_part'],
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
        version=dict(
            # TODO: There are a lot of implications when sorting record results
            # by versions and using the `_score`... Maybe there's some
            # elaborate ES syntax/API (eg. `constant_score`) to get a better
            # version-friendly sorted result.
            fields=['conceptrecid', 'relations.version.index'],
            title='Version',
            default_order='desc',
            order=7,
        )
    )
)
DEPOSIT_REST_SORT_OPTIONS['deposits'].update(
    dict(
        version=dict(
            # FIXME: No `_score` in deposit search response...
            fields=['conceptrecid', 'relations.version.index'],
            title='Version',
            default_order='desc',
            order=7,
        )
    )
)
RECORDS_REST_SORT_OPTIONS.update(OPENAIRE_REST_SORT_OPTIONS)
RECORDS_REST_SORT_OPTIONS.update(DEPOSIT_REST_SORT_OPTIONS)

#: Default sort for records REST API.
RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(query='bestmatch', noquery='mostrecent'),
)
RECORDS_REST_DEFAULT_SORT.update(OPENAIRE_REST_DEFAULT_SORT)
RECORDS_REST_DEFAULT_SORT.update(DEPOSIT_REST_DEFAULT_SORT)

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
                terms=dict(field="filetype"),
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
            file_type=terms_filter('filetype'),
            keywords=terms_filter('keywords'),
            subtype=terms_filter('resource_type.subtype'),
            type=terms_filter('resource_type.type'),
        )
    )
)
RECORDS_REST_FACETS.update(OPENAIRE_REST_FACETS)
RECORDS_REST_FACETS.update(DEPOSIT_REST_FACETS)

RECORDS_REST_ELASTICSEARCH_ERROR_HANDLERS = {
    'query_parsing_exception': (
        'invenio_records_rest.views'
        ':elasticsearch_query_parsing_exception_handler'
    ),
    'token_mgr_error': (
        'invenio_records_rest.views'
        ':elasticsearch_query_parsing_exception_handler'
    ),
}
"""Handlers for ElasticSearch error codes."""

# Previewer
# =========
#: Basic bundle which includes Font-Awesome/Bootstrap.
PREVIEWER_BASE_CSS_BUNDLES = ['zenodo_theme_css']
#: Basic bundle which includes Bootstrap/jQuery.
PREVIEWER_BASE_JS_BUNDLES = ['zenodo_theme_js']
#: Number of bytes read by CSV previewer to validate the file.
PREVIEWER_CSV_VALIDATION_BYTES = 2 * 1024
#: Max file size to preview for images
PREVIEWER_MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024

# OAI-PMH
# =======
#: Index to use for the OAI-PMH server.
OAISERVER_RECORD_INDEX = 'records'
#: OAI identifier prefix
OAISERVER_ID_PREFIX = 'oai:zenodo.org:'
#: Managed OAI identifier prefixes
OAISERVER_MANAGED_ID_PREFIXES = [OAISERVER_ID_PREFIX,
                                 'oai:openaire.cern.ch:', ]
#: Number of records to return per page in OAI-PMH results.
OAISERVER_PAGE_SIZE = 100
#: Increase resumption token expire time.
OAISERVER_RESUMPTION_TOKEN_EXPIRE_TIME = 2 * 60
#: PIDStore fetcher for OAI ID control numbers
OAISERVER_CONTROL_NUMBER_FETCHER = 'zenodo_record_fetcher'
#: Support email for OAI-PMH.
OAISERVER_ADMIN_EMAILS = [SUPPORT_EMAIL]
#: Do not register signals to automatically update records on updates.
OAISERVER_REGISTER_RECORD_SIGNALS = False
#: Do not register signals to automatically update records on oaiset updates.
OAISERVER_REGISTER_OAISET_SIGNALS = False
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
    'datacite': {
        'namespace': 'http://datacite.org/schema/kernel-3',
        'schema': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_datacite_v31',
    },
    'oai_datacite': {
        'namespace': 'http://datacite.org/schema/kernel-3',
        'schema': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_oai_datacite',
    },
    'oai_datacite3': {
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

# REST
# ====
#: Enable CORS support.
REST_ENABLE_CORS = True

# OAuth2 Server
# =============
#: Include '$' and "'" to cover various issues with search.
OAUTH2SERVER_ALLOWED_URLENCODE_CHARACTERS = '=&;:%+~,*@!()/?$\'"'
"""Special characters that should be valid inside a query string."""

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
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SCHEMES = [
    'pbkdf2_sha512', 'sha512_crypt', 'invenio_aes_encrypted_email']
SECURITY_DEPRECATED_PASSWORD_SCHEMES = [
    'sha512_crypt', 'invenio_aes_encrypted_email']

# Search
# ======
#: Default API endpoint for search UI.
SEARCH_UI_SEARCH_API = "/api/records/"
#: Accept header fro search-js
SEARCH_UI_SEARCH_MIMETYPE = "application/vnd.zenodo.v1+json"
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
    "postgresql+psycopg2://zenodo:zenodo@localhost/zenodo")
#: Do not print SQL queries to console.
SQLALCHEMY_ECHO = False
#: Track modifications to objects.
SQLALCHEMY_TRACK_MODIFICATIONS = True

# StatsD
# ======
#: Default StatsD host (i.e. no request timing)
STATSD_HOST = None
#: Default StatsD port
STATSD_PORT = 8125
#: Default StatsD port
STATSD_PREFIX = "zenodo"

# Proxy configuration
#: Number of proxies in front of application.
WSGI_PROXIES = 0

#: Set the session cookie to be secure - should be set to true in production.
SESSION_COOKIE_SECURE = False

# Indexer
# =======
#: Provide a custom record_to_index function for invenio-indexer
INDEXER_RECORD_TO_INDEX = "zenodo.modules.indexer.utils.record_to_index"
INDEXER_SCHEMA_TO_INDEX_MAP = {
    'records-record-v1.0.0': 'record-v1.0.0',
    'licenses-license-v1.0.0': 'license-v1.0.0',
    'grants-grant-v1.0.0': 'grant-v1.0.0',
    'deposits-records-record-v1.0.0': 'deposit-record-v1.0.0',
    'funders-funder-v1.0.0': 'funder-v1.0.0',
}
