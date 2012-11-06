# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os
from invenio.messages import gettext_set_language
from invenio.config import CFG_WEBSUBMIT_STORAGEDIR, CFG_SITE_ADMIN_EMAIL

try:
    from invenio.config import CFG_OPENAIRE_CURATORS as MAIN_CFG_OPENAIRE_CURATORS
except ImportError:
    MAIN_CFG_OPENAIRE_CURATORS = ""

CFG_OPENAIRE_PROJECT_INFORMATION_KB = 'json_projects'
""" Name of knowledge base for storing EU project information (JSON dictionary). """

CFG_OPENAIRE_PROJECT_DESCRIPTION_KB = 'projects'
""" Name of knowledge base for storing EU project description. """

CFG_OPENAIRE_DEPOSIT_PATH = os.path.join(CFG_WEBSUBMIT_STORAGEDIR, 'OpenAIRE')
""" Path where to store in-progress submission. """

CFG_OPENAIRE_MANDATORY_PROJECTS = True
""" Determine if EU FP7 project metadata is required. """

CFG_METADATA_STATES = ('ok', 'error', 'warning', 'empty')
"""
Field states used during form validation.

Note: Currently unused in code, but useful for defining which strings might be
returned as metadata status.
"""

CFG_PUBLICATION_STATES = (
    'initialized',
    'edited',
    'submitted',
    'pendingapproval',
    'approved',
    'rejected'
)
"""
States for a in-progress submission.
"""

CFG_OPENAIRE_CURATORS = []
""" List of curator email addresses. """
if MAIN_CFG_OPENAIRE_CURATORS.strip():
    CFG_OPENAIRE_CURATORS = [x.strip(
    ) for x in MAIN_CFG_OPENAIRE_CURATORS.split(",")]

# =================
# Publication types
# =================


def CFG_OPENAIRE_PUBLICATION_TYPES(ln):
    """
    Publication types

    @param ln: Language for human readable version of publication types.
    @return: Dictionary with type ids as keys and type titles as values.
    """
    _ = gettext_set_language(ln)

    return [
        ('publishedArticle', _("Published article")),
        #('preprint', _("Preprint")),
        ('report', _("Report")),
        ('thesis', _("Thesis")),
        #('workingPaper', _("Working paper")),
        ('book', _("Book")),
        ('bookpart', _("Book chapter/part of book")),
        #('periodicalContribution', _("Periodical contribution")),
        ('conferenceContribution', _("Conference contribution")),
        #('generalTalk', _("General talk")),
        #('patent', _("Patent")),
        ('data', _("Dataset")),
    ]

CFG_OPENAIRE_PUBLICATION_TYPES_KEYS = [x[0] for x in CFG_OPENAIRE_PUBLICATION_TYPES(
    'en')]
CFG_OPENAIRE_DEFAULT_PUBLICATION_TYPE = 'publishedArticle'
CFG_OPENAIRE_CC0_PUBLICATION_TYPES = ['data', ]

# ===============
# Metadata fields
# ===============

CFG_METADATA_FIELDS = (
    'title',
    'original_title',
    'authors',
    'abstract',
    'original_abstract',
    'language',
    'access_rights',
    'embargo_date',
    'publication_date',
    'journal_title',
    'volume',
    'pages',
    'issue',
    'keywords',
    'notes',
    'doi',
    'publication_type',
    'report_pages_no',
    'accept_cc0_license',
    'related_publications',
    'related_datasets',
    'publisher',
    'place',
    'report_type',
    'thesis_type',
    'extra_report_numbers',
    'isbn',
    'dataset_publisher',
    'supervisors',
    'university',
    'book_title',
    'book_pages',
    'contribution_type',
    'meeting_title',
    'meeting_acronym',
    'meeting_dates',
    'meeting_town',
    'meeting_country',
    'meeting_country',
    'meeting_url',
)
""" List of metadata fields, used in eg washing of URL parameters. """

CFG_METADATA_FIELDS_COMMON = (
    'publication_type',
    'authors',
    'title',
    'abstract',
    'language',
    'original_title',
    'original_abstract',
    'publication_date',
    'keywords',
    'notes',
    'doi',
    # TODO: Where is project?
)
""" List of metadata fields, common to all types of publications """

CFG_METADATA_FIELDS_GROUPS = {
    'publishedArticle': ['ACCESS_RIGHTS', 'JOURNAL', 'RELATED_DATA'],
    'preprint': [],
    'report': ['ACCESS_RIGHTS', 'PAGES_NO', 'REPORT', 'IMPRINT', 'ISBN', 
               'RELATED_DATA'],
    'thesis': ['ACCESS_RIGHTS','PAGES_NO', 'RELATED_DATA','THESIS', 'IMPRINT'],
    'workingPaper': [],
    'book': ['ACCESS_RIGHTS', 'PAGES_NO', 'RELATED_DATA', 'IMPRINT', 'ISBN'],
    'bookpart': ['ACCESS_RIGHTS', 'PAGES_NO', 'RELATED_DATA', 'BOOKPART'],
    'periodicalContribution': [],
    'conferenceContribution': ['ACCESS_RIGHTS', 'RELATED_DATA', 'MEETING'],
    'generalTalk': [],
    'patent': [],
    'data': ['CC0', 'DATASET', 'RELATED_PUBS'],
}
"""
Mapping of publication type to grouping of fields.

A group of fields can e.g. be JOURNAL for representing journal_title, volume,
pages and issue. This is used in the engine to generate MARC. Each group
is used to switch on/off part of the MARC generation.
"""

# =======================
# Controlled vocabularies
# =======================


def CFG_ACCESS_RIGHTS(ln):
    """
    Access rights for publication.

    @param ln: Language for human readable version of access right.
    @return: Dictionary with access right ids as keys and access right titles as values.
    """
    _ = gettext_set_language(ln)
    return [
        ('closedAccess', _("Closed access")),
        ('embargoedAccess', _("Embargoed access")),
        ('restrictedAccess', _("Restricted access")),
        ('openAccess', _("Open access")),
        ('cc0', _("Creative Commons Zero (CC0)")),
    ]
CFG_ACCESS_RIGHTS_KEYS = [x[0] for x in CFG_ACCESS_RIGHTS('en')]
CFG_DEFAULT_ACCESS_RIGHTS = 'closedAccess'


def CFG_OPENAIRE_REPORT_TYPES(ln):
    """
    Report types
    """
    _ = gettext_set_language(ln)
    return [
        ('projectDeliverable', _("Project deliverable")),
        ('other', _("Other")),
    ]

CFG_OPENAIRE_REPORT_TYPES_KEYS = [x[0] for x in CFG_OPENAIRE_REPORT_TYPES('en')]
CFG_OPENAIRE_DEFAULT_REPORT_TYPE = 'other'

def CFG_OPENAIRE_THESIS_TYPES(ln):
    """
    Report types
    """
    _ = gettext_set_language(ln)
    return [
        ('bachelorThesis', _("Bachelor thesis")),
        ('masterThesis', _("Master thesis")),
        ('doctoralThesis', _("Doctoral thesis")),
    ]

CFG_OPENAIRE_THESIS_TYPES_KEYS = [x[0] for x in CFG_OPENAIRE_THESIS_TYPES('en')]
CFG_OPENAIRE_DEFAULT_THESIS_TYPE = 'bachelorThesis'


def CFG_OPENAIRE_CONFERENCE_TYPES(ln):
    """
    Conference contribution types
    """
    _ = gettext_set_language(ln)
    return [
        ('proceedingArticle', _("Proceedings article")),
        ('poster', _("Poster")),
        ('conferencePaper', _("Conference paper")),
        ('conferenceTalk', _("Conference talk")),
    ]

CFG_OPENAIRE_CONFERENCE_TYPES_KEYS = [x[0] for x in CFG_OPENAIRE_CONFERENCE_TYPES('en')]
CFG_OPENAIRE_DEFAULT_CONFERENCE_TYPE = 'proceedingArticle'
