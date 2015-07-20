# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Zenodo configuration.

Instance independent configuration (e.g. which extensions to load) is defined
in ``zenodo.config'' while instance dependent configuration (e.g. database
host etc.) is defined in an optional ``zenodo.instance_config'' which
can be installed by a separate package.

This config module is loaded by the Flask application factory via an entry
point specified in the setup.py::

    entry_points={
        'invenio.config': [
            "zenodo = zenodo.config"
        ]
    },
"""

from __future__ import unicode_literals

import os
import sys

from datetime import timedelta

from celery.schedules import crontab

from invenio.base.config import EXTENSIONS

import pkg_resources

DEPRECATION_WARNINGS = True


def _(x):
    """Identity function for string extraction."""
    return x

PACKAGES = [
    'zenodo.base',
    'zenodo.demosite',
    'zenodo.modules.deposit',
    'zenodo.modules.github',
    'zenodo.modules.communities',
    'zenodo.modules.preservationmeter',
    'zenodo.modules.citationformatter',
    'zenodo.modules.grants',
    'zenodo.modules.accessrequests',
    'zenodo.modules.quotas',
    'invenio.modules.access',
    'invenio.modules.accounts',
    'invenio.modules.alerts',
    'invenio.modules.apikeys',
    'invenio.modules.authorprofiles',
    'invenio.modules.baskets',
    'invenio.modules.bulletin',
    'invenio.modules.circulation',
    'invenio.modules.classifier',
    'invenio.modules.cloudconnector',
    'invenio.modules.comments',
    'invenio.modules.communities',
    'invenio.modules.converter',
    'invenio.modules.dashboard',
    'invenio.modules.deposit',
    'invenio.modules.documentation',
    'invenio.modules.documents',
    'invenio.modules.editor',
    'invenio.modules.encoder',
    'invenio.modules.exporter',
    'invenio.modules.formatter',
    'invenio.modules.groups',
    'invenio.modules.indexer',
    'invenio.modules.jsonalchemy',
    'invenio.modules.knowledge',
    'invenio.modules.linkbacks',
    'invenio.modules.matcher',
    'invenio.modules.merger',
    'invenio.modules.messages',
    'invenio.modules.oaiharvester',
    'invenio.modules.oairepository',
    'invenio.modules.oauth2server',
    'invenio.modules.oauthclient',
    'invenio.modules.pages',
    'invenio.modules.pidstore',
    'invenio.modules.previewer',
    'invenio.modules.ranker',
    'invenio.modules.records',
    'invenio.modules.redirector',
    'invenio.modules.refextract',
    'invenio.modules.scheduler',
    'invenio.modules.search',
    'invenio.modules.sequencegenerator',
    'invenio.modules.sorter',
    'invenio.modules.statistics',
    'invenio.modules.submit',
    'invenio.modules.sword',
    'invenio.modules.tags',
    'invenio.modules.textminer',
    'invenio.modules.tickets',
    'invenio.modules.upgrader',
    'invenio.modules.uploader',
    'invenio.modules.webhooks',
    'invenio.modules.workflows',
    'invenio.base',
]

EXTENSIONS += [
    'zenodo.ext.deprecation_warnings:disable_deprecation_warnings',
]

PACKAGES_EXCLUDE = []

TEST_SUITES = [
    'zenodo.modules.deposit.testsuite',
    'zenodo.modules.github.testsuite',
    'zenodo.modules.preservationmeter.testsuite',
    'zenodo.modules.citationformatter.testsuite',
    # Run after records have been created by other tests
    'zenodo.base.testsuite',
    'zenodo.testsuite',
    'zenodo.modules.accessrequests.testsuite',
]


OAUTHCLIENT_REMOTE_APPS = dict(
    github=dict(
        title='GitHub',
        description='Software collaboration platform, with one-click software '
                    'preservation in Zenodo.',
        icon='fa fa-github',
        authorized_handler="zenodo.modules.github.views.handlers:authorized",
        disconnect_handler="zenodo.modules.github.views.handlers:disconnect",
        signup_handler=dict(
            info="zenodo.modules.github.views.handlers:account_info",
            setup="zenodo.modules.github.views.handlers:account_setup",
            view="invenio.modules.oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={
                'scope': 'user:email,admin:repo_hook,read:org'
            },
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_url="https://github.com/login/oauth/access_token",
            access_token_method='POST',
            authorize_url="https://github.com/login/oauth/authorize",
            app_key="GITHUB_APP_CREDENTIALS",
        )
    ),
    orcid=dict(
        title='ORCID',
        description='Connecting Research and Researchers.',
        icon='',
        authorized_handler="invenio.modules.oauthclient.handlers"
                           ":authorized_signup_handler",
        disconnect_handler="invenio.modules.oauthclient.handlers"
                           ":disconnect_handler",
        signup_handler=dict(
            info="invenio.modules.oauthclient.contrib.orcid:account_info",
            setup="invenio.modules.oauthclient.contrib.orcid:account_setup",
            view="invenio.modules.oauthclient.handlers:signup_handler",
        ),
        params=dict(
            request_token_params={'scope': '/authenticate'},
            base_url='https://pub.orcid.org/',
            request_token_url=None,
            access_token_url="https://pub.orcid.org/oauth/token",
            access_token_method='POST',
            authorize_url="https://orcid.org/oauth/authorize?show_login=true",
            app_key="ORCID_APP_CREDENTIALS",
            content_type="application/json",
        )
    ),
)

GITHUB_APP_CREDENTIALS = dict(
    consumer_key="changeme",
    consumer_secret="changeme",
)

ORCID_APP_CREDENTIALS = dict(
    consumer_key="changeme",
    consumer_secret="changeme",
)

CFG_PREVIEW_PREFERENCE = {
    '.pdf': ['pdfjs'],
    '.zip': ['zip'],
    '.md': ['mistune'],
    '.csv': ['csv_dthreejs'],
}

CFG_SORTER_CONFIGURATION = pkg_resources.resource_filename(
    'zenodo.base.sorterext', 'sorter.cfg'
)


DEPOSIT_TYPES = [
    "zenodo.modules.deposit.workflows.upload:upload",
]
DEPOSIT_DEFAULT_TYPE = "zenodo.modules.deposit.workflows.upload:upload"

COMMUNITIES_PARENT_NAME = 'Communities'
COMMUNITIES_PARENT_NAME_PROVISIONAL = 'Communities'
COMMUNITIES_PORTALBOXES = [
    'communities/portalbox_main.html',
    'communities/portalbox_upload.html'
]
COMMUNITIES_PORTALBOXES_PROVISIONAL = [
    'communities/portalbox_provisional.html',
]
COMMUNITIES_DISPLAYED_PER_PAGE = 20
COMMUNITIES_DEFAULT_SORTING_OPTION = 'ranking'
COMMUNITIES_PERIODIC_TASKS = {
    'ranking_deamon': {
        'run_every': timedelta(minutes=60),
    },
}

WEBHOOKS_DEBUG_RECEIVER_URLS = {
    'github': 'http://github.zenodo.ultrahook.com?access_token=%(token)s',
}

CFG_BIBSCHED_TASKLET_PACKAGES = [
    'invenio.legacy.bibsched.tasklets',
    'zenodo.legacy.tasklets',
]

RECORDS_BREADCRUMB_TITLE_KEY = 'title'

# Debug toolbar configuration
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
CFG_EMAIL_BACKEND = "flask_email.backends.console.Mail"

APACHE_CERTIFICATE_FILE = os.path.join(sys.prefix, 'etc/certs/localhost.crt')
APACHE_CERTIFICATE_KEYFILE = os.path.join(
    sys.prefix, 'etc/certs/localhost.key'
)
APACHE_ALIAS_EXCLUDES = ["/admin/"]

# Default database name
CFG_DATABASE_NAME = "zenodo"
CFG_DATABASE_USER = "zenodo"

# Name
CFG_SITE_NAME = "Zenodo"
CFG_SITE_NAME_INTL = dict(
    en="Zenodo",
)
CFG_SITE_LANGS = ["en"]
CFG_SITE_TAG = "LOCAL"
CFG_SITE_EMERGENCY_EMAIL_ADDRESSES = {'*': 'team@zenodo.org'}

CFG_SITE_ADMIN_EMAIL = "zenodo-admin@cern.ch"
CFG_SITE_SUPPORT_EMAIL = "info@zenodo.org"
CFG_WEBALERT_ALERT_ENGINE_EMAIL = "info@zenodo.org"
CFG_WEBCOMMENT_ALERT_ENGINE_EMAIL = "info@zenodo.org"
CFG_WEBCOMMENT_DEFAULT_MODERATOR = "info@zenodo.org"
CFG_BIBAUTHORID_AUTHOR_TICKET_ADMIN_EMAIL = "info@zenodo.org"
CFG_BIBCATALOG_SYSTEM_EMAIL_ADDRESS = "info@zenodo.org"
CFG_OPENAIRE_CURATORS = ["team@zenodo.org"]

CFG_GOOGLE_SITE_VERIFICATION = [
    "5fPGCLllnWrvFxH9QWI0l1TadV7byeEvfPcyK2VkS_s",
    "Rp5zp04IKW-s1IbpTOGB7Z6XY60oloZD5C3kTM-AiY4",
]
DEPOSIT_DROPBOX_API_KEY = "72dpqrjvx71mqyu"
CFG_BIBFORMAT_ADD_THIS_ID = "ra-4dc80cde118f4dad"

DEPOSIT_MAX_UPLOAD_SIZE = 2147483648
CFG_OPENAIRE_FILESIZE_NOTIFICATION = 10485760

# CFG_BROKER_URL = "amqp://openairenext:openairenext@localhost:5672/" \
#     "openairenext_vhost"
CFG_CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

CELERYBEAT_SCHEDULE = {
    # Every 15 minutes
    'communities-ranking': dict(
        task='invenio.modules.communities.tasks.RankingTask',
        schedule=timedelta(minutes=15),
    ),
    # Every 15 minutes
    'metrics-afs': dict(
        task='zenodo.modules.quotas.tasks.collect_metric',
        schedule=crontab(minute='*/15'),
        args=('zenodo.modules.quotas.metrics.afs:AFSVolumeMetric', ),
    ),
    # Every 5
    'metrics-bibsched': dict(
        task='zenodo.modules.quotas.tasks.collect_metric',
        schedule=crontab(minute='*/5'),
        args=('zenodo.modules.quotas.metrics.bibsched:BibSchedMetric', ),
    ),
    # Every hour
    'metrics-accounts': dict(
        task='zenodo.modules.quotas.tasks.collect_metric',
        schedule=crontab(minute=0, hour='*/1'),
        args=('zenodo.modules.quotas.metrics.accounts:AccountsMetric', ),
    ),
    # Every 3 hour
    'metrics-communities': dict(
        task='zenodo.modules.quotas.tasks.collect_metric',
        schedule=crontab(minute=1, hour='*/3'),
        args=('zenodo.base.metrics.communities:CommunitiesMetric', ),
    ),
    'metrics-pidstore': dict(
        task='zenodo.modules.quotas.tasks.collect_metric',
        schedule=crontab(minute=1, hour='*/3'),
        args=('zenodo.base.metrics.pidstore:PIDStoreMetric', ),
    ),
    'publish-metrics': dict(
        task='zenodo.modules.quotas.tasks.publish_metrics',
        schedule=crontab(minute='*/15'),
        args=('zenodo.modules.quotas.publishers.cern:CERNPublisher', ),
    ),
    # # Every 12 hours
    # 'metrics-deposit': dict(
    #     task='zenodo.modules.quotas.tasks.collect_metric',
    #     schedule=crontab(minute=1),
    #     args=('zenodo.modules.quotas.metrics.deposit:DepositMetric', ),
    # ),
    # Every Sunday
    'harvest-grants': dict(
        task='zenodo.modules.grants.tasks.harvest_openaire_grants',
        schedule=crontab(minute='3', hour='0', day_of_week='mon'),
        args=(),
    ),
}

QUOTAS_PUBLISH_METRICS = [
    dict(type='System', id=CFG_SITE_NAME, metric='bibsched.tasks'),
    dict(type='System', id=CFG_SITE_NAME, metric='accounts.num'),
    dict(type='System', id=CFG_SITE_NAME, metric='accounts.logins6h'),
    dict(type='System', id=CFG_SITE_NAME, metric='communities.num'),
    dict(type='System', id=CFG_SITE_NAME, metric='pidstore.numdois'),
]
QUOTAS_XSLS_API_URL = "http://xsls-dev.cern.ch"
QUOTAS_XSLS_SERVICE_ID = "zenododev"
QUOTAS_XSLS_AVAILABILITY = 'zenodo.base.metrics:availability'

CFG_WEBSEARCH_ENABLE_OPENGRAPH = True
CFG_WEBSEARCH_DISPLAY_NEAREST_TERMS = False
CFG_WEBSEARCH_PUBLIC_RECORD_EXTRA_CHECK = True

CFG_BIBDOCFILE_FILESYSTEM_BIBDOC_GROUP_LIMIT = 1000

CFG_OPENAIRE_SITE = 1
# CFG_WEBSTYLE_TEMPLATE_SKIN = "openaire"
CFG_WEBSTYLE_HTTP_USE_COMPRESSION = 1

CFG_WEBCOMMENT_ALLOW_SHORT_REVIEWS = 0
CFG_WEBCOMMENT_ALLOW_REVIEWS = 0
CFG_WEBCOMMENT_USE_RICH_TEXT_EDITOR = True

CFG_WEBSEARCH_VIEWRESTRCOLL_POLICY = "ANY"
CFG_WEBSEARCH_USE_MATHJAX_FOR_FORMATS = "hb,hd"
CFG_MATHJAX_HOSTING = "cdn"

CFG_WEBSESSION_CACHE_GUESTS = 1
CFG_WEBSESSION_EXPIRY_LIMIT_DEFAULT_GUESTS = 1
CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS = 3
CFG_WEBSESSION_NOT_CONFIRMED_EMAIL_ADDRESS_EXPIRE_IN_DAYS = 3

CFG_WEB_API_KEY_ALLOWED_URL = [('api/deposit/\?', 0, False), ]
CFG_WEB_API_KEY_ENABLE_SIGNATURE = False

CFG_OAI_METADATA_FORMATS = {
    'oai_dc': (
        'XOAIDC',
        'http://www.openarchives.org/OAI/1.1/dc.xsd',
        'http://purl.org/dc/elements/1.1/'
    ),
    'marcxml': (
        'XOAIMARC',
        'http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd',
        'http://www.loc.gov/MARC21/slim'
    ),
    'datacite': (
        'DCITE',
        'http://schema.datacite.org/meta/kernel-2.2/metadata.xsd',
        'http://datacite.org/schema/kernel-2.2'
    ),
    'oai_datacite': (
        'OAIDCI',
        'http://schema.datacite.org/meta/kernel-2.2/metadata.xsd',
        'http://datacite.org/schema/kernel-2.2'
    ),
    'datacite3': (
        'DCITE3',
        'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'http://datacite.org/schema/kernel-3'
    ),
    'oai_datacite3': (
        'OAIDC3',
        'http://schema.datacite.org/meta/kernel-3/metadata.xsd',
        'http://datacite.org/schema/kernel-3'
    ),
}

CFG_OAI_ID_PREFIX = "zenodo.org"
CFG_OAI_SAMPLE_IDENTIFIER = "oai:zenodo.org:103"
CFG_OAI_FILTER_RESTRICTED_RECORDS = False
CFG_OAI_IDENTIFY_DESCRIPTION = """<description>
  <eprints xmlns="http://www.openarchives.org/OAI/1.1/eprints"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.openarchives.org/OAI/1.1/eprints
                               http://www.openarchives.org/OAI/1.1/eprints.xsd">
      <content>
       <text>Please refer to the link below.</text>
       <URL>http://zenodo.org/policies</URL>
      </content>
      <metadataPolicy>
       <text>Please refer to the link below.</text>
       <URL>http://zenodo.org/policies</URL>
      </metadataPolicy>
      <dataPolicy>
       <text>Please refer to the link below.</text>
       <URL>http://zenodo.org/policies</URL>
      </dataPolicy>
      <submissionPolicy>
       <text>Please refer to the link below.</text>
       <URL>http://zenodo.org/policies</URL>
      </submissionPolicy>
  </eprints>
 </description>"""

CFG_OAI_LOAD = 10
CFG_OAI_SLEEP = 3
CFG_OAI_DELETED_POLICY = "no"

CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS = 0

CFG_BIBFORMAT_HIDDEN_TAGS = ["595", "8560", "65017"]
CFG_BIBFORMAT_HIDDEN_RECJSON_FIELDS = ["owner"]

# Record access control based on user
CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_EMAILS_IN_TAGS = []
CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_USERIDS_IN_TAGS = ["8560_w"]
CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS = []
CFG_ACC_GRANT_VIEWER_RIGHTS_TO_USERIDS_IN_TAGS = []

CFG_DATACITE_SITE_URL = "http://zenodo.org"
CFG_DATACITE_USERNAME = ""
CFG_DATACITE_PASSWORD = ""

# Don't commit anything. Testmode implies prefix is set to 10.5072
CFG_DATACITE_TESTMODE = False

# Test prefix (use with or without test mode):
CFG_DATACITE_DOI_PREFIX = "10.5072"

PIDSTORE_DATACITE_RECORD_DOI_FIELD = 'doi'
PIDSTORE_DATACITE_OUTPUTFORMAT = 'dcite3'
PIDSTORE_DATACITE_SITE_URL = "http://zenodo.org"

SCHEMAORG_MAP = dict(
    publication='http://schema.org/ScholarlyArticle',
    poster='http://schema.org/CreativeWork',
    presentation='http://schema.org/CreativeWork',
    dataset='http://schema.org/Dataset',
    image='http://schema.org/ImageObject',
    video='http://schema.org/VideoObject',
    book='http://schema.org/Book',
    section='http://schema.org/ScholarlyArticle',
    conferencepaper='http://schema.org/ScholarlyArticle',
    article='http://schema.org/ScholarlyArticle',
    deliverable='http://schema.org/CreativeWork',
    milestone='http://schema.org/CreativeWork',
    patent='http://schema.org/CreativeWork',
    preprint='http://schema.org/ScholarlyArticle',
    proposal='http://schema.org/CreativeWork',
    report='http://schema.org/ScholarlyArticle',
    thesis='http://schema.org/ScholarlyArticle',
    technicalnote='http://schema.org/ScholarlyArticle',
    softwaredocumentation='http://schema.org/',
    workingpaper='http://schema.org/ScholarlyArticle',
    other='http://schema.org/CreativeWork',
    figure='http://schema.org/CreativeWork',
    plot='http://schema.org/CreativeWork',
    drawing='http://schema.org/CreativeWork',
    diagram='http://schema.org/CreativeWork',
    photo='http://schema.org/Photograph',
    software='http://schema.org/Code',
)

CFG_ACCESS_RIGHTS = [
    ('closedAccess', _("Closed access")),
    ('embargoedAccess', _("Embargoed access")),
    ('restrictedAccess', _("Restricted access")),
    ('openAccess', _("Open access")),
    ('cc0', _("Creative Commons Zero (CC0)")),
    ('closed', _("Closed access")),
    ('embargoed', _("Embargoed access")),
    ('restricted', _("Restricted access")),
    ('open', _("Open access")),
]

CFG_OPENAIRE_PUBTYPE_MAP = [
    ('OPENAIRE', _("Published article")),
    ('PREPRINT', _("Preprint")),
    ('REPORT_PROJECTDELIVERABLE', _("Report")),
    ('REPORT_OTHER', _("Report")),
    ('BACHELORTHESIS', _("Thesis")),
    ('MASTERTHESIS', _("Thesis")),
    ('DOCTORALTHESIS', _("Thesis")),
    ('WORKINGPAPER', _("Working paper")),
    ('BOOK', _("Book")),
    ('BOOKPART', _("Part of book")),
    ('MEETING_PROCEEDINGSARTICLE', _("Proceedings article")),
    ('MEETING_POSTER', _("Poster")),
    ('MEETING_CONFERENCEPAPER', _("Conference paper")),
    ('MEETING_CONFERENCETALK', _("Talk")),
    ('DATA', _("Dataset")),
    ('publication', _("Publication")),
    ('poster', _("Poster")),
    ('presentation', _("Presentation")),
    ('dataset', _("Dataset")),
    ('image', _("image")),
    ('video', _("Video/Audio")),
    ('book', _('Book')),
    ('section', _('Book section')),
    ('conferencepaper', _('Conference paper')),
    ('article', _('Journal article')),
    ('deliverable', _('Project Deliverable')),
    ('milestone', _('Project Milestone')),
    ('patent', _('Patent')),
    ('preprint', _('Preprint')),
    ('proposal', _('Proposal')),
    ('report', _('Report')),
    ('thesis', _('Thesis')),
    ('technicalnote', _('Technical note')),
    ('softwaredocumentation', _('Software documentation')),
    ('workingpaper', _('Working paper')),
    ('other', _('Other')),
    ('figure', _('Figure')),
    ('plot', _('Plot')),
    ('drawing', _('Drawing')),
    ('diagram', _('Diagram')),
    ('photo', _('Photo')),
    ('other', _('Other')),
    ('software', _('Software')),
    ('lesson', _('Lesson')),
]

CFG_OPENAIRE_THESIS_TYPES = [
    ('bachelorThesis', _("Bachelor thesis")),
    ('masterThesis', _("Master thesis")),
    ('doctoralThesis', _("Doctoral thesis")),
]


# Demo site roles
DEF_DEMO_ROLES = [
]

DEF_DEMO_USER_ROLES = (
    ('info@zenodo.org', 'superadmin'),
)

DEF_DEMO_AUTHS = (
    ('anyuser', 'viewrestrcoll', {'collection': 'zenodo-public'}),
    ('superadmin', 'viewrestrcoll', {'collection': 'hidden'}),
)

try:
    from zenodo.instance_config import *  # noqa
except ImportError:
    pass
