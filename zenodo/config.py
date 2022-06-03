# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016, 2017, 2018 CERN.
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

    # ${VIRTUAL_ENV}/var/instance/invenio.cfg
    SUPPORT_EMAIL = "info@example.org"

Configuration variables
~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
from datetime import timedelta
from functools import partial

import jsonref
from celery.schedules import crontab
from flask_principal import ActionNeed
from invenio_access.permissions import Permission
from invenio_app.config import APP_DEFAULT_SECURE_HEADERS
from invenio_deposit.config import DEPOSIT_REST_DEFAULT_SORT, \
    DEPOSIT_REST_FACETS, DEPOSIT_REST_SORT_OPTIONS
from invenio_deposit.scopes import write_scope
from invenio_deposit.utils import check_oauth2_scope
from invenio_github.config import GITHUB_REMOTE_APP
from invenio_github.errors import CustomGitHubMetadataError
from invenio_oauthclient.contrib.orcid import REMOTE_APP as ORCID_REMOTE_APP
from invenio_openaire.config import OPENAIRE_REST_DEFAULT_SORT, \
    OPENAIRE_REST_ENDPOINTS, OPENAIRE_REST_FACETS, \
    OPENAIRE_REST_SORT_OPTIONS
from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_pidrelations.config import RelationType
from invenio_records_rest.facets import range_filter, terms_filter
from invenio_records_rest.sorter import geolocation_sort
from invenio_records_rest.utils import allow_all
from invenio_stats.aggregations import StatAggregator
from invenio_stats.processors import EventsIndexer
from invenio_stats.queries import ESTermsQuery
from zenodo_accessrequests.config import ACCESSREQUESTS_RECORDS_UI_ENDPOINTS

from zenodo.modules.github.schemas import CitationMetadataSchema
from zenodo.modules.records.facets import custom_metadata_filter, \
    geo_bounding_box_filter
from zenodo.modules.records.permissions import deposit_delete_permission_factory, \
    deposit_read_permission_factory, deposit_update_permission_factory, \
    record_create_permission_factory
from zenodo.modules.stats import current_stats_search_client
from zenodo.modules.theme.ext import useragent_and_ip_limit_key


def _(x):
    """Identity function for string extraction."""
    return x


#: System sender email address
ZENODO_SYSTEM_SENDER_EMAIL = 'system@zenodo.org'
#: Email address of admins
ZENODO_ADMIN_EMAIL = 'admin@zenodo.org'

#: Email address for support.
SUPPORT_EMAIL = "info@zenodo.org"
MAIL_SUPPRESS_SEND = True

# Application
# ===========
#: Disable Content Security Policy headers.
APP_DEFAULT_SECURE_HEADERS['content_security_policy'] = {}
# NOTE: These should be set explicitly inside ``invenio.cfg`` for development,
# if one wants to run wihtout ``FLASK_DEBUG`` enabled.
# APP_DEFAULT_SECURE_HEADERS['force_https'] = False
# APP_DEFAULT_SECURE_HEADERS['session_cookie_secure'] = False

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
#: DataCite updating rate.
DATACITE_UPDATING_RATE_PER_HOUR = 1000
#: DataCite max description length
DATACITE_MAX_DESCRIPTION_SIZE = 20000

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
CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
#: Default Celery result backend.
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
#: Accepted content types for Celery.
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
#: Custom task routing
CELERY_TASK_ROUTES = {
    'invenio_files_rest.tasks.verify_checksum': {'queue': 'low'},
    'zenodo.modules.sipstore.tasks.archive_sip': {'queue': 'low'},
    'zenodo_migrator.tasks.migrate_concept_recid_sips': {'queue': 'low'},
    'invenio_openaire.tasks.register_grant': {'queue': 'low'},
    'invenio_indexer.tasks.process_bulk_queue': {'queue': 'celery-indexer'}
}
#: Beat schedule
CELERY_BEAT_SCHEDULE = {
    'embargo-updater': {
        'task': 'zenodo.modules.records.tasks.update_expired_embargos',
        'schedule': crontab(minute=2, hour=0),
    },
    'indexer': {
        'task': 'invenio_indexer.tasks.process_bulk_queue',
        'schedule': timedelta(minutes=5),
        'kwargs': {
            'es_bulk_kwargs': {'raise_on_error': False},
        },
    },
    'openaire-updater': {
        'task': 'zenodo.modules.utils.tasks.update_search_pattern_sets',
        'schedule': timedelta(hours=12),
    },
    'cleanup-indexed-deposits': {
        'task': 'zenodo.modules.deposit.tasks.cleanup_indexed_deposits',
        'schedule': timedelta(hours=2),
    },
    'session-cleaner': {
        'task': 'invenio_accounts.tasks.clean_session_table',
        'schedule': timedelta(hours=24),
    },
    'file-checks': {
        'task': 'invenio_files_rest.tasks.schedule_checksum_verification',
        'schedule': timedelta(hours=1),
        'kwargs': {
            'batch_interval': {'hours': 1},
            'frequency': {'days': 14},
            'max_count': 0,
            # Query taking into account only files with URI prefixes defined by
            # the FILES_REST_CHECKSUM_VERIFICATION_URI_PREFIXES config variable
            'files_query':
                'zenodo.modules.utils.files.checksum_verification_files_query',
        },
    },
    'hard-file-checks': {
        'task': 'invenio_files_rest.tasks.schedule_checksum_verification',
        'schedule': timedelta(hours=1),
        'kwargs': {
            'batch_interval': {'hours': 1},
            # Manually check and calculate checksums of files biannually
            'frequency': {'days': 180},
            # Split batches based on total files size
            'max_size': 0,
            # Query taking into account only files with URI prefixes defined by
            # the FILES_REST_CHECKSUM_VERIFICATION_URI_PREFIXES config variable
            'files_query':
                'zenodo.modules.utils.files.checksum_verification_files_query',
            # Actual checksum calculation, instead of relying on a EOS query
            'checksum_kwargs': {'use_default_impl': True},
        },
    },
    'sitemap-updater': {
        'task': 'zenodo.modules.sitemap.tasks.update_sitemap_cache',
        'schedule': timedelta(hours=24)
    },
    'file-integrity-report': {
        'task': 'zenodo.modules.utils.tasks.file_integrity_report',
        'schedule': crontab(minute=0, hour=7),  # Every day at 07:00 UTC
    },
    'datacite-metadata-updater': {
        'task': (
            'zenodo.modules.records.tasks.schedule_update_datacite_metadata'),
        'schedule': timedelta(hours=1),
        'kwargs': {
            'max_count': DATACITE_UPDATING_RATE_PER_HOUR,
        }
    },
    'export': {
        'task': 'zenodo.modules.exporter.tasks.export_job',
        'schedule': crontab(minute=0, hour=4, day_of_month=1),
        'kwargs': {
            'job_id': 'records',
        }
    },
    # Stats
    'stats-process-events': {
        'task': 'invenio_stats.tasks.process_events',
        'schedule': timedelta(minutes=30),
        'args': [('record-view', 'file-download')],
    },
    'stats-aggregate-events': {
        'task': 'invenio_stats.tasks.aggregate_events',
        'schedule': timedelta(hours=3),
        'args': [(
            'record-view-agg', 'record-view-all-versions-agg',
            'record-download-agg', 'record-download-all-versions-agg',
        )],
    },
    'stats-update-record-statistics': {
        'task': 'zenodo.modules.stats.tasks.update_record_statistics',
        'schedule': crontab(minute=0, hour=1),  # Every day at 01:00 UTC
    },
    'stats-export': {
        'task': 'zenodo.modules.stats.tasks.export_stats',
        'schedule': crontab(minute=0, hour=4),
        'kwargs': {
            'retry': True,
        }
    },
    'github-tokens-refresh': {
        'task': 'invenio_github.tasks.refresh_accounts',
        'schedule': crontab(minute=0, hour=3),
        'kwargs': {
            'expiration_threshold': {
                # TODO: Remove when invenio-github v1.0.0a19 is released
                'days': 6 * 30,
            },
        }
    }
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
ACCESS_CACHE = 'invenio_cache:current_cache'
#: Disable JSON Web Tokens
ACCOUNTS_JWT_ENABLE = False

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
#: GitHub metadata file
GITHUB_METADATA_FILE = '.zenodo.json'
#: GitHub citation file
GITHUB_CITATION_FILE = 'CITATION.cff'
#: Github Citation Metadata Schema
GITHUB_CITATION_METADATA_SCHEMA = partial(
    CitationMetadataSchema, context={'replace_refs': True})
#: GitHub error handlers
GITHUB_ERROR_HANDLERS = [
    (
        'zenodo.modules.deposit.errors.VersioningFilesError',
        'zenodo.modules.github.error_handlers.versioning_files_error'
    ),
    (
       'github3.exceptions.AuthenticationFailed',
       'zenodo.modules.github.error_handlers.authentification_failed'
    ),
    (
        'zenodo.modules.deposit.errors.MarshmallowErrors',
        'zenodo.modules.github.error_handlers.marshmallow_error'
    ),
    (
        CustomGitHubMetadataError,
        'zenodo.modules.github.error_handlers.invalid_json_error'
    ),
    (
        jsonref.JsonRefError,
        'zenodo.modules.github.error_handlers.invalid_ref_error'
    ),
    (
        Exception,
        'zenodo.modules.github.error_handlers.default_error'
    ),
]
#   (
#        'invenio_github.errors.RepositoryAccessError',
#        'zenodo.modules.github.error_handlers.repository_access_error'
#    ),
#    (
#        'sqlalchemy.lib.sqlalchemy.orm.exc.StaleDataError',
#        'zenodo.modules.github.error_handlers.stale_data_error'
#    ),
#    (
#        'sqlalchemy.lib.sqlalchemy.exc.InvalidRequestError',
#        'zenodo.modules.github.error_handlers.invalid_request_error'
#    ),
#    (
#        'elasticsearch.exceptions.ConnectionError',
#        'zenodo.modules.github.error_handlers.connection_error'
#    ),
#    (
#        'elasticsearch.exceptions.ClientError',
#        'zenodo.modules.github.error_handlers.client_error'
#    ),
#    (
#        'sqlalchemy.lib.sqlalchemy.exc.IntegrityError',
#        'zenodo.modules.github.error_handlers.integrity_error'
#    ),
#    (
#        'ForbiddenError',
#        'zenodo.modules.github.error_handlers.forbidden_error'
#    ),
#    (
#        'ServerError',
#        'zenodo.modules.github.error_handlers.server_error'
#    )

#: SIPStore
SIPSTORE_GITHUB_AGENT_JSONSCHEMA = 'sipstore/agent-githubclient-v1.0.0.json'
#: Set OAuth client application config.
SIPSTORE_ARCHIVER_DIRECTORY_BUILDER = \
    'zenodo.modules.sipstore.utils.archive_directory_builder'
#: Set the builder for archived SIPs directory structure
SIPSTORE_ARCHIVER_LOCATION_NAME = 'archive'
#: Set the name of the Location object holding the archive URI
SIPSTORE_ARCHIVER_METADATA_TYPES = ['json', 'marcxml']
#: Set the names of SIPMetadataType(s), which are to be archived.
SIPSTORE_ARCHIVER_SIPFILE_NAME_FORMATTER = \
    'invenio_sipstore.archivers.utils.secure_sipfile_name_formatter'
#: Set the SIPFile name formatter to write secure filenames
SIPSTORE_ARCHIVER_SIPMETADATA_NAME_FORMATTER = \
    'zenodo.modules.sipstore.utils.sipmetadata_name_formatter'
#: Set the SIPMetadata name formatter: "record-{json/marcxml}.{json/xml}"
SIPSTORE_BAGIT_TAGS = [
    ('Source-Organization', 'European Organization for Nuclear Research'),
    ('Organization-Address', 'CERN, CH-1211 Geneva 23, Switzerland'),
    ('Bagging-Date', None),  # Autogenerated
    ('Payload-Oxum', None),  # Autogenerated
    ('External-Identifier', None),  # Autogenerated
    ('External-Description', ("BagIt archive of Zenodo record. "
        "Description of the payload structure and data interpretation "
        "available at https://doi.org/10.5281/zenodo.841781")),
]

SIPSTORE_ARCHIVER_WRITING_ENABLED = False
#: Flag controlling whether writing files to disk should be enabled

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
    'dataset': 'opendoar____::2659',
    'software': 'opendoar____::2659',
    'other': 'opendoar____::2659'
}
#: OpenAIRE ID namespace prefixes for Zenodo.
OPENAIRE_NAMESPACE_PREFIXES = {
    'publication': 'od______2659',
    'dataset': 'od______2659',
    'software': 'od______2659',
    'other': 'od______2659'
}
#: OpenAIRE API endpoint.
OPENAIRE_API_URL = 'http://dev.openaire.research-infrastructures.eu/is/mvc/api/results'
OPENAIRE_API_URL_BETA = None
#: OpenAIRE API endpoint username.
OPENAIRE_API_USERNAME = None
#: OpenAIRE API endpoint password.
OPENAIRE_API_PASSWORD = None
#: URL to OpenAIRE portal.
OPENAIRE_PORTAL_URL = 'https://explore.openaire.eu'
#: OpenAIRE community identifier prefix.
OPENAIRE_COMMUNITY_IDENTIFIER_PREFIX = 'https://openaire.eu/communities'
#: Enable sending published records for direct indexing at OpenAIRE.
OPENAIRE_DIRECT_INDEXING_ENABLED = False

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
#: Specific templates for the various deposit form elements.
DEPOSIT_FORM_TEMPLATES = {
    'actions': 'actions.html',
    'array': 'array.html',
    'button': 'button.html',
    'checkbox': 'checkbox.html',
    'ckeditor': 'ckeditor.html',
    'default': 'default.html',
    'fieldset': 'fieldset.html',
    'radios_inline': 'radios_inline.html',
    'radios': 'radios.html',
    'select': 'select.html',
    'strapselect': 'strapselect.html',
    'textarea': 'textarea.html',
    'uiselect': 'uiselect.html',
    'grantselect': 'grantselect.html',
}

#: Allow list of contributor types.
DEPOSIT_CONTRIBUTOR_TYPES = [
    dict(label='Contact person', marc='prc', datacite='ContactPerson'),
    dict(label='Data collector', marc='col', datacite='DataCollector'),
    dict(label='Data curator', marc='cur', datacite='DataCurator'),
    dict(label='Data manager', marc='dtm', datacite='DataManager'),
    dict(label='Distributor', marc='dst', datacite='Distributor'),
    dict(label='Editor', marc='edt', datacite='Editor'),
    dict(label='Hosting institution', marc='his',
         datacite='HostingInstitution'),
    dict(label='Other', marc='oth', datacite='Other'),
    dict(label='Producer', marc='pro', datacite='Producer'),
    dict(label='Project leader', marc='pdr', datacite='ProjectLeader'),
    dict(label='Project manager', marc='rth', datacite='ProjectManager'),
    dict(label='Project member', marc='rtm', datacite='ProjectMember'),
    dict(label='Registration agency', marc='cor',
         datacite='RegistrationAgency'),
    dict(label='Registration authority', marc='cor',
         datacite='RegistrationAuthority'),
    dict(label='Related person', marc='oth', datacite='RelatedPerson'),
    dict(label='Research group', marc='rtm', datacite='ResearchGroup'),
    dict(label='Researcher', marc='res', datacite='Researcher'),
    dict(label='Rights holder', marc='cph', datacite='RightsHolder'),
    dict(label='Sponsor', marc='spn', datacite='Sponsor'),
    dict(label='Supervisor', marc='dgs', datacite='Supervisor'),
    dict(label='Work package leader', marc='led',
         datacite='WorkPackageLeader'),
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
        message="Deleted successfully."
    ),
    discard=dict(
        message="Changes discarded successfully."
    ),
    publish=dict(
        message="Published successfully."
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
        'view_imp': 'zenodo.modules.deposit.views.default_view_method',
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

# Default SIP agent factory
SIPSTORE_AGENT_FACTORY = 'zenodo.modules.sipstore.utils:build_agent_info'

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

ZENODO_REANA_HOSTS = ["reana.cern.ch", "reana-qa.cern.ch", "reana-dev.cern.ch"]
ZENODO_REANA_LAUNCH_URL_BASE = "https://reana.cern.ch/launch"
ZENODO_REANA_BADGE_IMG_URL = "https://www.reana.io/static/img/badges/launch-on-reana.svg"
ZENODO_REANA_BADGES_ENABLED = True

#: Mapping of old export formats to new content type.
ZENODO_RECORDS_EXPORTFORMATS = {
    'dcite': dict(
        title='DataCite XML',
        serializer='zenodo.modules.records.serializers.datacite_v41',
    ),
    'dcite3': dict(
        title='DataCite XML',
        serializer='zenodo.modules.records.serializers.datacite_v31',
    ),
    'dcite4': dict(
        title='DataCite XML',
        serializer='zenodo.modules.records.serializers.datacite_v41',
    ),
    'hm': dict(
        title='MARC21 XML',
        serializer='zenodo.modules.records.serializers.marcxml_v1',
    ),
    'hx': dict(
        title='BibTeX',
        serializer='zenodo.modules.records.serializers.bibtex_v1',
    ),
    'xd': dict(
        title='Dublin Core',
        serializer='zenodo.modules.records.serializers.dc_v1',
    ),
    'xm': dict(
        title='MARC21 XML',
        serializer='zenodo.modules.records.serializers.marcxml_v1',
    ),
    'json': dict(
        title='JSON',
        serializer='zenodo.modules.records.serializers.json_v1',
    ),
    'schemaorg_jsonld': dict(
        title='JSON-LD (schema.org)',
        serializer='zenodo.modules.records.serializers.schemaorg_jsonld_v1',
    ),
    'csl': dict(
        title='Citation Style Language JSON',
        serializer='zenodo.modules.records.serializers.csl_v1',
    ),
    'cp': dict(
        title='Citation',
        serializer='zenodo.modules.records.serializers.citeproc_v1',
    ),
    # Generic serializer
    'ef': dict(
        title='Formats',
        serializer='zenodo.modules.records.serializers.extra_formats_v1',
    ),
    'geojson': dict(
        title='GeoJSON',
        serializer='zenodo.modules.records.serializers.geojson_v1',
    ),
    'dcat': dict(
        title='DCAT',
        serializer='zenodo.modules.records.serializers.dcat_v1',
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
    recid_thumbnail=dict(
        pid_type='recid',
        route='/record/<pid_value>/thumb<thumbnail_size>',
        view_imp='zenodo.modules.records.views.record_thumbnail',
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
    recid_files=dict(
        pid_type='recid',
        route='/record/<pid_value>/files/<path:filename>',
        view_imp='invenio_records_files.utils.file_download_ui',
        record_class='zenodo.modules.records.api:ZenodoRecord',
    ),
    recid_extra_formats=dict(
        pid_type='recid',
        route='/record/<pid_value>/formats',
        view_imp='zenodo.modules.records.views.record_extra_formats',
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

#: URI prefixes of files their checksums should be verified
FILES_REST_CHECKSUM_VERIFICATION_URI_PREFIXES = [
    # 'root://eospublic'
]
#: URL template for generating URLs outside the application/request context
FILES_REST_ENDPOINT = '{scheme}://{host}/api/files/{bucket}/{key}'


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
            'application/ld+json': (
                'zenodo.modules.records.serializers.schemaorg_jsonld_v1_response'),
            'application/marcxml+xml': (
                'zenodo.modules.records.serializers.marcxml_v1_response'),
            'application/x-bibtex': (
                'zenodo.modules.records.serializers.bibtex_v1_response'),
            'application/x-datacite+xml': (
                'zenodo.modules.records.serializers.datacite_v31_response'),
            'application/x-datacite-v41+xml': (
                'zenodo.modules.records.serializers.datacite_v41_response'),
            'application/x-dc+xml': (
                'zenodo.modules.records.serializers.dc_v1_response'),
            'application/vnd.citationstyles.csl+json': (
                'zenodo.modules.records.serializers.csl_v1_response'),
            'application/dcat+xml': (
                'zenodo.modules.records.serializers.dcat_response'),
            'text/x-bibliography': (
                'zenodo.modules.records.serializers.citeproc_v1_response'),
            'application/vnd.geo+json': (
                'zenodo.modules.records.serializers.geojson_v1_response'),
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

# Add record serializer aliases for use with the "?format=<mimetype>" parameter
RECORDS_REST_ENDPOINTS['recid']['record_serializers_aliases'] = {
    s: s for s in RECORDS_REST_ENDPOINTS['recid']['record_serializers']
}

# Default OpenAIRE API endpoints.
RECORDS_REST_ENDPOINTS.update(OPENAIRE_REST_ENDPOINTS)

# Add fuzzy matching for licenses
OPENDEFINITION_REST_ENDPOINTS['od_lic']['suggesters']['text']['completion']['fuzzy'] = True
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
        mostviewed=dict(
            fields=['-_stats.version_views'],
            title='Most viewed',
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
        distance=dict(
            title='Distance',
            fields=[geolocation_sort('location.point', 'center', 'km')],
            default_order='asc',
            display=False,
            order=2,
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
        distance=dict(
            title=_('Distance'),
            fields=[geolocation_sort('location.point', 'center', 'km')],
            default_order='asc',
            display=False,
            order=2,
        ),
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
        default_aggs=['access_right', 'type', 'file_type', 'keywords'],
        aggs=dict(
            type=dict(
                terms=dict(field='resource_type.type'),
                aggs=dict(
                    subtype=dict(
                        terms=dict(size=20, field='resource_type.subtype'),
                    )
                )
            ),
            access_right=dict(
                terms=dict(field='access_right'),
            ),
            file_type=dict(
                terms=dict(field='filetype'),
            ),
            keywords=dict(
                terms=dict(field='keywords'),
            ),
            communities=dict(
                terms=dict(field='communities'),
            ),
            related_identifiers_type=dict(
                terms=dict(field='related.resource_type.type'),
                aggs=dict(
                    related_identifiers_subtype=dict(
                        terms=dict(field='related.resource_type.subtype'),
                    )
                )
            ),
            publication_date=dict(
                date_histogram=dict(
                    field='publication_date',
                    interval='1y',
                    format='yyyy'
                )
            ),
        ),
        filters=dict(
            communities=terms_filter('communities'),
            custom=custom_metadata_filter('custom'),
            provisional_communities=terms_filter('provisional_communities'),
            bounds=geo_bounding_box_filter(
                'bounds', 'locations.point', type='indexed'),
            publication_date=range_filter(
                field='publication_date',
                format='yyyy'
            ),
        ),
        post_filters=dict(
            access_right=terms_filter('access_right'),
            file_type=terms_filter('filetype'),
            keywords=terms_filter('keywords'),
            subtype=terms_filter('resource_type.subtype'),
            type=terms_filter('resource_type.type'),
            related_identifiers_type=terms_filter(
                'related.resource_type.type'),
            related_identifiers_subtype=terms_filter(
                'related.resource_type.subtype'),
        )
    )
)

#: Update deposit facets as well
DEPOSIT_REST_FACETS['deposits'].setdefault('filters', {})
DEPOSIT_REST_FACETS['deposits']['filters'].update(dict(
    communities=terms_filter('communities'),
    custom=custom_metadata_filter('custom'),
    provisional_communities=terms_filter('provisional_communities'),
    locations=geo_bounding_box_filter(
        'locations', 'locations.point', type='indexed'),
))

# TODO: Remove `grants` aggregations until
# https://github.com/zenodo/zenodo/issues/1909 is fixed
OPENAIRE_REST_FACETS.pop('grants', None)
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
#: List of previewers (adds IIIF previewer).
PREVIEWER_PREFERENCE = [
    'csv_dthreejs',
    'iiif_image',
    'simple_image',
    # 'json_prismjs',
    # 'xml_prismjs',
    'mistune',
    'pdfjs',
    # 'ipynb',
    'zip',
]

# IIIF
# ====
#: Improve quality of image resampling using better algorithm
IIIF_RESIZE_RESAMPLE = 'PIL.Image:BICUBIC'

#: Use the Redis storage backend for caching IIIF images
# TODO: Fix Python 3 caching key issue to enable:
#   https://github.com/inveniosoftware/flask-iiif/issues/66
# IIIF_CACHE_HANDLER = 'flask_iiif.cache.redis:ImageRedisCache'

# Redis storage for thumbnails caching.
IIIF_CACHE_REDIS_URL = CACHE_REDIS_URL

# Precached thumbnails
CACHED_THUMBNAILS = {
    '10': '10,',
    '50': '50,',
    '100': '100,',
    '250': '250,',
    '750': '750,',
    '1200': '1200,'
    }

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
    'datacite4': {
        'namespace': 'http://datacite.org/schema/kernel-4',
        'schema': 'http://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_datacite_v41',
    },
    'datacite3': {
        'namespace': 'http://datacite.org/schema/kernel-3',
        'schema': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_datacite_v31',
    },
    'datacite': {
        'namespace': 'http://datacite.org/schema/kernel-4',
        'schema': 'http://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_datacite_v41',
    },
    'dcat': {
        'namespace': 'https://www.w3.org/ns/dcat',
        'schema': 'http://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_dcat_v1',
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
    'oai_datacite4': {
        'namespace': 'http://datacite.org/schema/kernel-4',
        'schema': 'http://schema.datacite.org/meta/kernel-4.1/metadata.xsd',
        'serializer':
            'zenodo.modules.records.serializers.oaipmh_oai_datacite_v41',
    },
    'oai_dc': {
        'namespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
        'serializer': 'zenodo.modules.records.serializers.oaipmh_oai_dc',
    }
}
# Relative URL to XSL Stylesheet, placed under `modules/records/static`.
OAISERVER_XSL_URL = '/static/xsl/oai2.xsl'

# REST
# ====
#: Enable CORS support.
REST_ENABLE_CORS = True
#: Enable specifying export format via querystring
REST_MIMETYPE_QUERY_ARG_NAME = 'format'

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

#: Session and User ID headers
ACCOUNTS_USERINFO_HEADERS = True

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
#: Angular template for rendering search errors.
SEARCH_UI_JSTEMPLATE_ERROR = "templates/zenodo_search_ui/error.html"
#: Default Elasticsearch document type.
SEARCH_DOC_TYPE_DEFAULT = None
#: Do not map any keywords.
SEARCH_ELASTIC_KEYWORD_MAPPING = {}
#: Only create indexes we actually need.
SEARCH_MAPPINGS = [
    'deposits',
    'funders',
    'grants',
    'licenses',
    'records',
]
#: ElasticSearch index prefix
SEARCH_INDEX_PREFIX = 'zenodo-dev-'

# Communities
# ===========
#: Override templates to use custom search-js
COMMUNITIES_COMMUNITY_TEMPLATE = "zenodo_theme/communities/base.html"
#: Override templates to use custom search-js
COMMUNITIES_CURATE_TEMPLATE = "zenodo_theme/communities/curate.html"
#: Override templates to use custom search-js
COMMUNITIES_SEARCH_TEMPLATE = "zenodo_theme/communities/search.html"
#: Override detail page template
COMMUNITIES_DETAIL_TEMPLATE = "zenodo_theme/communities/detail.html"
#: Override about page template
COMMUNITIES_ABOUT_TEMPLATE = "zenodo_theme/communities/about.html"

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
THEME_SITEURL = "http://127.0.0.1:5000"
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

THEME_MATHJAX_CDN = (
    '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js'
    '?config=TeX-AMS-MML_HTMLorMML'
)

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

# Stats
# =====
STATS_EVENTS = {
    'file-download': {
        'signal': 'invenio_files_rest.signals.file_downloaded',
        'templates': 'zenodo.modules.stats.templates.events',
        'event_builders': [
            'invenio_stats.contrib.event_builders.file_download_event_builder',
            'zenodo.modules.stats.event_builders:skip_deposit',
            'zenodo.modules.stats.event_builders:add_record_metadata',
        ],
        'cls': EventsIndexer,
        'params': {
            'preprocessors': [
                'invenio_stats.processors:flag_robots',
                # Don't index robot events
                lambda doc: doc if not doc['is_robot'] else None,
                'invenio_stats.processors:flag_machines',
                'invenio_stats.processors:anonymize_user',
                'invenio_stats.contrib.event_builders:build_file_unique_id',
            ],
            # Keep only 1 file download for each file and user every 30 sec
            'double_click_window': 30,
            # Create one index per month which will store file download events
            'suffix': '%Y-%m',
        },
    },
    'record-view': {
        'signal': 'invenio_records_ui.signals.record_viewed',
        'templates': 'zenodo.modules.stats.templates.events',
        'event_builders': [
            'invenio_stats.contrib.event_builders.record_view_event_builder',
            'zenodo.modules.stats.event_builders:skip_deposit',
            'zenodo.modules.stats.event_builders:add_record_metadata',
        ],
        'cls': EventsIndexer,
        'params': {
            'preprocessors': [
                'invenio_stats.processors:flag_robots',
                # Don't index robot events
                lambda doc: doc if not doc['is_robot'] else None,
                'invenio_stats.processors:flag_machines',
                'invenio_stats.processors:anonymize_user',
                'invenio_stats.contrib.event_builders:build_record_unique_id',
            ],
            # Keep only 1 file download for each file and user every 30 sec
            'double_click_window': 30,
            # Create one index per month which will store file download events
            'suffix': '%Y-%m',
        },
    },
}
#: Enabled aggregations from 'zenoodo.modules.stats.registrations'
STATS_AGGREGATIONS = {
    'record-view-agg': dict(
        templates='zenodo.modules.stats.templates.aggregations',
        cls=StatAggregator,
        params=dict(
            client=current_stats_search_client,
            event='record-view',
            field='recid',
            interval='day',
            index_interval='month',
            copy_fields=dict(
                record_id='record_id',
                recid='recid',
                conceptrecid='conceptrecid',
                doi='doi',
                conceptdoi='conceptdoi',
                communities=lambda d, _: (
                    list(d.communities) if d.communities else None),
                owners=lambda d, _: (list(d.owners) if d.owners else None),
                is_parent=lambda *_: False
            ),
            metric_fields=dict(
                unique_count=('cardinality', 'unique_session_id',
                              {'precision_threshold': 1000}),
            )
        )
    ),
    'record-view-all-versions-agg': dict(
        templates='zenodo.modules.stats.templates.aggregations',
        cls=StatAggregator,
        params=dict(
            client=current_stats_search_client,
            event='record-view',
            field='conceptrecid',
            interval='day',
            index_interval='month',
            copy_fields=dict(
                conceptrecid='conceptrecid',
                conceptdoi='conceptdoi',
                communities=lambda d, _: (
                    list(d.communities) if d.communities else None),
                owners=lambda d, _: (list(d.owners) if d.owners else None),
                is_parent=lambda *_: True
            ),
            metric_fields=dict(
                unique_count=(
                    'cardinality', 'unique_session_id',
                    {'precision_threshold': 1000}),
            )
        )
    ),
    'record-download-agg': dict(
        templates='zenodo.modules.stats.templates.aggregations',
        cls=StatAggregator,
        params=dict(
            client=current_stats_search_client,
            event='file-download',
            field='recid',
            interval='day',
            index_interval='month',
            copy_fields=dict(
                bucket_id='bucket_id',
                record_id='record_id',
                recid='recid',
                conceptrecid='conceptrecid',
                doi='doi',
                conceptdoi='conceptdoi',
                communities=lambda d, _: (
                    list(d.communities) if d.communities else None),
                owners=lambda d, _: (list(d.owners) if d.owners else None),
                is_parent=lambda *_: False
            ),
            metric_fields=dict(
                unique_count=('cardinality', 'unique_session_id',
                              {'precision_threshold': 1000}),
                volume=('sum', 'size', {}),
            )
        )
    ),
    'record-download-all-versions-agg': dict(
        templates='zenodo.modules.stats.templates.aggregations',
        cls=StatAggregator,
        params=dict(
            client=current_stats_search_client,
            event='file-download',
            field='conceptrecid',
            interval='day',
            copy_fields=dict(
                conceptrecid='conceptrecid',
                conceptdoi='conceptdoi',
                communities=lambda d, _: (
                    list(d.communities) if d.communities else None),
                owners=lambda d, _: (list(d.owners) if d.owners else None),
                is_parent=lambda *_: True
            ),
            metric_fields=dict(
                unique_count=(
                    'cardinality', 'unique_session_id',
                    {'precision_threshold': 1000}),
                volume=('sum', 'size', {}),
            )
        )
    ),
}


def stats_queries_permission_factory(query_name, params):
    """Queries permission factory."""
    return Permission(ActionNeed('admin-access'))


#: Enabled queries from 'zenoodo.modules.stats.registrations'
STATS_QUERIES = {
    'record-view': dict(
        cls=ESTermsQuery,
        permission_factory=stats_queries_permission_factory,
        params=dict(
            index='stats-record-view',
            doc_type='record-view-day-aggregation',
            copy_fields=dict(
                record_id='record_id',
                recid='recid',
                conceptrecid='conceptrecid',
                doi='doi',
                conceptdoi='conceptdoi',
                communities='communities',
                owners='owners',
                is_parent='is_parent'
            ),
            required_filters=dict(
                recid='recid',
            ),
            metric_fields=dict(
                count=('sum', 'count', {}),
                unique_count=('sum', 'unique_count', {}),
            )
        )
    ),
    'record-view-all-versions': dict(
        cls=ESTermsQuery,
        permission_factory=stats_queries_permission_factory,
        params=dict(
            index='stats-record-view',
            doc_type='record-view-day-aggregation',
            copy_fields=dict(
                conceptrecid='conceptrecid',
                conceptdoi='conceptdoi',
                communities='communities',
                owners='owners',
                is_parent='is_parent'
            ),
            query_modifiers=[
                lambda query, **_: query.filter('term', is_parent=True)
            ],
            required_filters=dict(
                conceptrecid='conceptrecid',
            ),
            metric_fields=dict(
                count=('sum', 'count', {}),
                unique_count=('sum', 'unique_count', {}),
            )
        )
    ),
    'record-download': dict(
        cls=ESTermsQuery,
        permission_factory=stats_queries_permission_factory,
        params=dict(
            index='stats-file-download',
            doc_type='file-download-day-aggregation',
            copy_fields=dict(
                bucket_id='bucket_id',
                record_id='record_id',
                recid='recid',
                conceptrecid='conceptrecid',
                doi='doi',
                conceptdoi='conceptdoi',
                communities='communities',
                owners='owners',
                is_parent='is_parent'
            ),
            required_filters=dict(
                recid='recid',
            ),
            metric_fields=dict(
                count=('sum', 'count', {}),
                unique_count=('sum', 'unique_count', {}),
                volume=('sum', 'volume', {}),
            )
        ),
    ),
    'record-download-all-versions': dict(
        cls=ESTermsQuery,
        permission_factory=stats_queries_permission_factory,
        params=dict(
            index='stats-file-download',
            doc_type='file-download-day-aggregation',
            copy_fields=dict(
                conceptrecid='conceptrecid',
                conceptdoi='conceptdoi',
                communities='communities',
                owners='owners',
                is_parent='is_parent'
            ),
            query_modifiers=[
                lambda query, **_: query.filter('term', is_parent=True)
            ],
            required_filters=dict(
                conceptrecid='conceptrecid',
            ),
            metric_fields=dict(
                count=('sum', 'count', {}),
                unique_count=('sum', 'unique_count', {}),
                volume=('sum', 'volume', {}),
            )
        )
    ),
}

# Queues
# ======
QUEUES_BROKER_URL = CELERY_BROKER_URL

# Proxy configuration
#: Number of proxies in front of application.
WSGI_PROXIES = 0

#: Set the session cookie to be secure - should be set to true in production.
SESSION_COOKIE_SECURE = False

# Configuration for limiter.
RATELIMIT_STORAGE_URL = CACHE_REDIS_URL

RATELIMIT_PER_ENDPOINT = {
    'zenodo_frontpage.index': '10 per second',
    'security.login': '10 per second',
    'zenodo_redirector.contact': '10 per second',
    'zenodo_support.support': '10 per second',
    # Badge endpoints
    'invenio_github_badge.latest_doi_old': '10 per second',
    'invenio_github_badge.latest_doi': '10 per second',
    'invenio_github_badge.index': '10 per second',
    'invenio_github_badge.index_old': '10 per second',
    'invenio_formatter_badges.badge': '10 per second',
}

RATELIMIT_KEY_FUNC = useragent_and_ip_limit_key

# Error templates
THEME_429_TEMPLATE = "zenodo_errors/429.html"
THEME_400_TEMPLATE = "zenodo_errors/400.html"

failed_login_msg = (_("Login failed; Invalid user or password."), 'error')

SECURITY_MSG_USER_DOES_NOT_EXIST = failed_login_msg
SECURITY_MSG_PASSWORD_NOT_SET = failed_login_msg
SECURITY_MSG_INVALID_PASSWORD = failed_login_msg
SECURITY_MSG_CONFIRMATION_REQUIRED = failed_login_msg

ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD=1000
ZENODO_RECORDS_SEARCH_SAFELIST=False
