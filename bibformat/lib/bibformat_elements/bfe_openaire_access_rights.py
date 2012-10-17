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

import cgi
import time

from invenio.config import CFG_SITE_URL
from invenio.openaire_deposit_engine import CFG_ACCESS_RIGHTS
from invenio.messages import gettext_set_language

def format_element(bfo):
    ln = bfo.lang
    _ = gettext_set_language(ln)
    access_rights = bfo.field('542__l')
    embargo = ''
    if access_rights == 'embargoedAccess':
        embargo = bfo.field('942__a')
        if embargo <= time.strftime("%Y-%m-%d"):
            access_rights = 'openAccess'

    submitter = bfo.field('8560_f')
    email = """<a href="mailto:%s">%s</a>""" % (cgi.escape(submitter, True), cgi.escape(submitter))

    if access_rights == 'embargoedAccess':
        ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: this document will be available as Open Access after %(embargo)s.")
    elif access_rights == 'closedAccess':
        ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is close.")
    elif access_rights == 'openAccess':
        ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is open.")
    elif access_rights == 'restrictedAccess':
        ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is open but with some restrictions. To access the document, please contact %(email)s.")
    elif access_rights == 'cc0':
        ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: To the extent possible under law, the authors have waived all copyright and related or neighbouring rights to this data. %(cc0link)s")


    return ret % {
        'x_fmt_s': "<strong>",
        'x_fmt_e': "</strong>",
        'access': CFG_ACCESS_RIGHTS(ln)[access_rights],
        'cc0link' : """<a href="http://creativecommons.org/publicdomain/zero/1.0/"><img src="%s/img/cc-zero.png"></a>""" % CFG_SITE_URL,
        'embargo': embargo,
        'email': email
    }

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
