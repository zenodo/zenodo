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

from invenio.config import CFG_WEBSUBMIT_STORAGEDIR, CFG_SITE_ADMIN_EMAIL, \
    CFG_OPENAIRE_CURATORS as MAIN_CFG_OPENAIRE_CURATORS
from invenio.messages import gettext_set_language
import os

CFG_OPENAIRE_PROJECT_INFORMATION_KB = 'json_projects'
""" Name of knowledge base for storing EU project information (JSON dictionary). """

CFG_OPENAIRE_PROJECT_DESCRIPTION_KB = 'projects'
""" Name of knowledge base for storing EU project description. """

CFG_OPENAIRE_DEPOSIT_PATH = os.path.join(CFG_WEBSUBMIT_STORAGEDIR, 'OpenAIRE')
""" Path where to store in-progress submission. """

CFG_OPENAIRE_MANDATORY_PROJECTS = True
""" Determine if EU FP7 project metadata is required. """

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
)
""" 
List of metadata fields, used in eg washing of URL parameters.
"""

CFG_METADATA_STATES = ('ok', 'error', 'warning', 'empty')
""" 
Field states used during form validation. 
TODO: Unused?
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
    CFG_OPENAIRE_CURATORS = [x.strip() for x in MAIN_CFG_OPENAIRE_CURATORS.split(",")]


def CFG_ACCESS_RIGHTS(ln):
    """
    Access rights for publication.
    
    @param ln: Language for human readable version of access right.
    @return: Dictionary with access right ids as keys and access right titles as values. 
    """
    _ = gettext_set_language(ln)
    return {
        'closedAccess': _("Closed access"),
        'embargoedAccess': _("Embargoed access"),
        'restrictedAccess': _("Restricted access"),
        'openAccess': _("Open access")
    }

def CFG_OPENAIRE_PUBLICATION_TYPES(ln):
    """
    Publication types
    
    @param ln: Language for human readable version of publication types.
    @return: Dictionary with type ids as keys and type titles as values. 
    """
    _ = gettext_set_language(ln)
    return {
        'publishedArticle': _("Published article"),
        'data': _("Data set"),
        'report': _("Report"),
    }
