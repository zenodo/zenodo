# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
Zenodo configuration
--------------------
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

# Define identity function for string extraction
_ = lambda x: x

PACKAGES = [
    'zenodo.base',
    'zenodo.modules.deposit',
    'zenodo.modules.communities',
    'invenio.modules.*',
]

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

RECORDS_BREADCRUMB_TITLE_KEY = 'title'

# Debug toolbar configuration
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
CFG_EMAIL_BACKEND = "flask.ext.email.backends.console.Mail"

# Default database name
CFG_DATABASE_NAME = "zenodo"
CFG_DATABASE_USER = "zenodo"

# Name
CFG_SITE_NAME = "ZENODO"
CFG_SITE_NAME_INTL = dict(
    en="ZENODO",
)
CFG_SITE_LANGS = ["en"]
CFG_SITE_TAG = "LOCAL"
CFG_SITE_EMERGENCY_EMAIL_ADDRESSES = {'*': '{{CFG_INVENIO_ADMIN}}'}

CFG_SITE_ADMIN_EMAIL = "admin@zenodo.org"
CFG_SITE_SUPPORT_EMAIL = "info@zenodo.org"
CFG_OPENAIRE_CURATORS = ["team@zenodo.org"]

CFG_GOOGLE_SITE_VERIFICATION = [
    "5fPGCLllnWrvFxH9QWI0l1TadV7byeEvfPcyK2VkS_s,Rp5zp04IKW-s1IbpTOGB7Z6XY60oloZD5C3kTM-AiY4",
]
CFG_DROPBOX_API_KEY = "72dpqrjvx71mqyu"
CFG_BIBFORMAT_ADD_THIS_ID = "ra-4dc80cde118f4dad"
#CFG_PIWIK_URL = "piwik.web.cern.ch/piwik/"
#CFG_PIWIK_SITE_ID = "57"

CFG_WEBDEPOSIT_MAX_UPLOAD_SIZE = 2147483648
CFG_OPENAIRE_FILESIZE_NOTIFICATION = 10485760

#CFG_BROKER_URL = "amqp://openairenext:openairenext@localhost:5672/openairenext_vhost"
CFG_CELERY_RESULT_BACKEND = "redis://localhost:6379/1"


CFG_WEBSEARCH_ENABLE_OPENGRAPH = True
CFG_WEBSEARCH_DISPLAY_NEAREST_TERMS = False

CFG_BIBDOCFILE_FILESYSTEM_BIBDOC_GROUP_LIMIT = 1000

CFG_OPENAIRE_SITE = 1
#CFG_WEBSTYLE_TEMPLATE_SKIN = "openaire"
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
    'marcxml': ('XOAIMARC', 'http://www.openarchives.org/OAI/1.1/dc.xsd', 'http://purl.org/dc/elements/1.1/'),
    'oai_dc': ('XOAIDC', 'http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd', 'http://www.loc.gov/MARC21/slim'),
    'datacite': ('DCITE', 'http://schema.datacite.org/meta/kernel-2.2/metadata.xsd', 'http://datacite.org/schema/kernel-2.2'),
    'oai_datacite': ('OAIDCI', 'http://schema.datacite.org/meta/kernel-2.2/metadata.xsd', 'http://datacite.org/schema/kernel-2.2'),
}

CFG_OAI_ID_PREFIX = "zenodo.org"
CFG_OAI_SAMPLE_IDENTIFIER = "oai:zenodo.org:103"
CFG_OAI_FILTER_RESTRICTED_RECORDS = False
CFG_OAI_IDENTIFY_DESCRIPTION = """<description>
   <oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier
                                       http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">
      <scheme>oai</scheme>
      <repositoryIdentifier>zenodo.org</repositoryIdentifier>
      <delimiter>:</delimiter>
      <sampleIdentifier>oai:zenodo.org:103</sampleIdentifier>
   </oai-identifier>
 </description>
 <description>
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

CFG_BIBFORMAT_HIDDEN_TAGS = "595,8560,65017"

CFG_DATACITE_SITE_URL = "http://zenodo.org"
CFG_DATACITE_USERNAME = ""
CFG_DATACITE_PASSWORD = ""

# Don't commit anything. Testmode implies prefix is set to 10.5072
CFG_DATACITE_TESTMODE = False

# Test prefix (use with or without test mode):
CFG_DATACITE_DOI_PREFIX = "10.5072"

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
    patent='http://schema.org/CreativeWork',
    preprint='http://schema.org/ScholarlyArticle',
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
    ('patent', _('Patent')),
    ('preprint', _('Preprint')),
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
]

CFG_OPENAIRE_THESIS_TYPES = [
    ('bachelorThesis', _("Bachelor thesis")),
    ('masterThesis', _("Master thesis")),
    ('doctoralThesis', _("Doctoral thesis")),
]

try:
    from zenodo.instance_config import *
except ImportError:
    pass
