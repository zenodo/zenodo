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

"""BibFormat element - Print link to push an entry to a remote server through SWORD
"""
__revision__ = "$Id$"

from flask import current_app
from invenio.utils.url import create_html_link
from invenio.modules.access.engine import acc_authorize_action

def format_element(bfo, remote_server_id, style, css_class, link_label="Push via Sword",):
    """
    Print link to push an entry to a remote server through SWORD

    @param remote_server_id: ID of the remove server to link to. When
                             not specified, link to BibSword page
                             allowing to select server.
    """
    CFG_SITE_URL = current_app.config['CFG_SITE_URL']

    user_info = bfo.user_info
    auth_code, auth_message = acc_authorize_action(user_info, 'runbibswordclient')
    if auth_code != 0:
        return ""

    sword_arguments = {'ln': bfo.lang,
                       'recid': bfo.recID}

    if remote_server_id:
        sword_arguments['id_remote_server'] = remote_server_id
    else:
        sword_arguments['status'] = 'select_server'

    linkattrd = {}
    if style != '':
        linkattrd['style'] = style
    if css_class != '':
        linkattrd['class'] = css_class

    return create_html_link(CFG_SITE_URL + '/bibsword',
                            sword_arguments,
                            link_label,
                            linkattrd=linkattrd)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
