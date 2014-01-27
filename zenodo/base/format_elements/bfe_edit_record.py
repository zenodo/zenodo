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

"""BibFormat element - Prints a link to BibEdit
"""
__revision__ = "$Id$"


from flask import current_app
from invenio.utils.url import create_html_link
from invenio.base.i18n import gettext_set_language
from invenio.legacy.bibedit.utils import user_can_edit_record_collection


def format_element(bfo, style, css_class):
    """
    Prints a link to BibEdit, if authorization is granted

    @param style: the CSS style to be applied to the link.
    @param css_class: the CSS class to be applied to the link.
    """
    _ = gettext_set_language(bfo.lang)

    out = ""

    user_info = bfo.user_info
    if user_can_edit_record_collection(user_info, bfo.recID):
        linkattrd = {}
        if style != '':
            linkattrd['style'] = style
        if css_class != '':
            linkattrd['class'] = css_class
        out += create_html_link(current_app.config['CFG_SITE_URL'] +
               '/%s/edit/?ln=%s#state=edit&recid=%s' % (current_app.config['CFG_SITE_RECORD'], bfo.lang, str(bfo.recID)),
               {},
               link_label="<i class=\"icon-pencil\"></i> %s" % _("Edit"),
               linkattrd=linkattrd)

    return out


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
