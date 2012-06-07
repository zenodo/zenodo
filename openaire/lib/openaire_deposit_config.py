# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
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
from invenio.config import CFG_WEBSUBMIT_STORAGEDIR, CFG_SITE_ADMIN_EMAIL, CFG_OPENAIRE_CURATORS as MAIN_CFG_OPENAIRE_CURATORS
from invenio.messages import gettext_set_language

CFG_OPENAIRE_PROJECT_INFORMATION_KB = 'json_projects'
CFG_OPENAIRE_PROJECT_DESCRIPTION_KB = 'projects'
CFG_OPENAIRE_DEPOSIT_PATH = os.path.join(CFG_WEBSUBMIT_STORAGEDIR, 'OpenAIRE')
CFG_OPENAIRE_CURATORS = [x.strip() for x in MAIN_CFG_OPENAIRE_CURATORS.split(",")] if MAIN_CFG_OPENAIRE_CURATORS.strip() else []

def CFG_ACCESS_RIGHTS(ln):
    _ = gettext_set_language(ln)
    return {
        'closedAccess': _("Closed access"),
        'embargoedAccess': _("Embargoed access"),
        'restrictedAccess': _("Restricted access"),
        'openAccess': _("Open access")}

CFG_METADATA_FIELDS = ('title', 'original_title', 'authors', 'abstract',
    'original_abstract', 'language', 'access_rights', 'embargo_date',
    'publication_date', 'journal_title', 'volume', 'pages', 'issue', 'keywords', 'notes', 'doi')

CFG_METADATA_STATES = ('ok', 'error', 'warning', 'empty')
CFG_PUBLICATION_STATES = ('initialized', 'edited', 'submitted', 'pendingapproval', 'approved', 'rejected')
CFG_OPENAIRE_MANDATORY_PROJECTS = True
