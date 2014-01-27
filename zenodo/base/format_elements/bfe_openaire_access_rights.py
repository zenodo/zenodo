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

import cgi
import time

from flask import current_app
from invenio.base.i18n import gettext_set_language


def format_element(bfo, as_label=False, only_restrictions=False):
    CFG_ACCESS_RIGHTS = current_app.config['CFG_ACCESS_RIGHTS']
    ln = bfo.lang
    _ = gettext_set_language(ln)
    access_rights = bfo.field('542__l')
    embargo = ''
    if access_rights in ('embargoedAccess', 'embargoed'):
        embargo = bfo.field('942__a')
        if embargo <= time.strftime("%Y-%m-%d"):
            access_rights = 'open'
        embargo = time.strftime("%d %B %Y", time.strptime(embargo, "%Y-%m-%d"))

    submitter = bfo.field('8560_f')
    email = """<a href="mailto:%s">%s</a>""" % (cgi.escape(submitter, True), cgi.escape(submitter))
    access = _(dict(current_app.config['CFG_ACCESS_RIGHTS'])[access_rights])

    if only_restrictions:
        if access_rights in ('embargoedAccess', 'embargoed'):
            return """<dt>Embargoed</dt><dd>Files available as <span class="label label-success">Open Access</span> after %s</dd>""" % embargo
        elif access_rights in ('restricteDaccess', 'restricted'):
            return """<dt>Restricted access</dt><dd>Please contact %s to access the files.</dd>""" % email
    elif as_label:
        if access_rights in ('embargoedAccess', 'embargoed'):
            return """<a href="/search?p=542__l:embargoed" class="label label-warning" rel="tooltip" title="Available as Open Access after %s">%s</a>""" % (embargo, _(access))
        elif access_rights in ('closeDaccess', 'closed'):
            return """<a href="/search?p=542__l:closed" class="label label-important">%s</a>""" % _(access)
        elif access_rights in ('openAccess', 'open'):
            return """<a href="/search?p=542__l:open" class="label label-success">%s</a>""" % _(access)
        elif access_rights in ('restricteDaccess', 'restricted'):
            return """<a href="/search?p=542__l:restricted" class="label label-warning">%s</a>""" % _(access)
        elif access_rights == 'cc0':
            return """<a class="label label-success">%s</a>""" % _(access)
    else:
        if access_rights in ('embargoedAccess', 'embargoed'):
            ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: this document will be available as Open Access after %(embargo)s.")
        elif access_rights in ('closeDaccess', 'closed'):
            ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is close.")
        elif access_rights in ('openAccess', 'open'):
            ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is open.")
        elif access_rights in ('restricteDaccess', 'restricted'):
            ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: the access to this document is open but with some restrictions. To access the document, please contact %(email)s.")
        elif access_rights == 'cc0':
            ret = _("%(x_fmt_s)s%(access)s%(x_fmt_e)s: To the extent possible under law, the authors have waived all copyright and related or neighbouring rights to this data. %(cc0link)s")

        return ret % {
            'x_fmt_s': "<strong>",
            'x_fmt_e': "</strong>",
            'access': access,
            'cc0link': """<a href="http://creativecommons.org/publicdomain/zero/1.0/"><img src="/img/cc-zero.png"></a>""",
            'embargo': embargo,
            'email': email
        }


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
