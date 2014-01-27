# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
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

"""BibFormat element - Prints a link to BibDocFile
"""
__revision__ = "$Id$"

from flask import current_app
from invenio.utils.url import create_html_link
from invenio.base.i18n import gettext_set_language
from invenio.modules.access.engine import acc_authorize_action


def format_element(bfo, style, css_class):
    """
    Prints a link to simple file management interface (BibDocFile), if
    authorization is granted.

    @param style: the CSS style to be applied to the link.
    """
    _ = gettext_set_language(bfo.lang)

    out = ""

    user_info = bfo.user_info
    (auth_code, auth_message) = acc_authorize_action(user_info,
                                                     'runbibdocfile')
    if auth_code == 0:
        linkattrd = {}
        if style != '':
            linkattrd['style'] = style
        if css_class != '':
            linkattrd['class'] = css_class
        out += create_html_link(current_app.config['CFG_SITE_URL'] + '/%s/managedocfiles' % current_app.config['CFG_SITE_RECORD'],
                         urlargd={'ln': bfo.lang,
                                  'recid': str(bfo.recID)},
                         link_label= """<i class="icon-file"></i> %s""" % _("Manage Files"),
                         linkattrd=linkattrd)
    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
