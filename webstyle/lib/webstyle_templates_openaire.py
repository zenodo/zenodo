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

"""
WebStyle templates. Customize the look of pages of Invenio
"""

import cgi

from invenio.config import \
    CFG_SITE_LANG, \
    CFG_SITE_NAME, \
    CFG_SITE_NAME_INTL, \
    CFG_SITE_SUPPORT_EMAIL, \
    CFG_SITE_SECURE_URL, \
    CFG_SITE_URL, \
    CFG_VERSION, \
    CFG_WEBSTYLE_INSPECT_TEMPLATES, \
    CFG_WEBSTYLE_TEMPLATE_SKIN
from invenio.messages import gettext_set_language, is_language_rtl
from invenio.dateutils import convert_datecvs_to_datestruct, \
    convert_datestruct_to_dategui
from invenio.webstyle_templates import Template as InvenioTemplate
from invenio.urlutils import create_html_link
from invenio.webinterface_handler_flask_utils import _

from flask import render_template
from bs4 import BeautifulSoup


class Template(InvenioTemplate):

    def tmpl_navtrailbox_body(self, ln, title, previous_links, separator,
                              prolog, epilog):
        """ Bootstrap friendly-Create navigation trail box body """
        if title == CFG_SITE_NAME_INTL.get(ln, CFG_SITE_NAME):
            return ""

        # First element
        breadcrumbs = [(_("Home"), CFG_SITE_URL), ]

        # Decode previous elements
        if previous_links:
            soup = BeautifulSoup(previous_links)
            for link in soup.find_all('a'):
                breadcrumbs.append((unicode(" ".join(link.contents)), link.get('href')))

        # Add head
        if title:
            breadcrumbs.append((title, ''))

        return render_template("legacy_navtrailbox_body.html",
                               breadcrumbs=breadcrumbs).encode('utf8')

    def tmpl_page(self, req, **kwargs):
        return render_template("legacy_page.html", **kwargs).encode('utf8')
