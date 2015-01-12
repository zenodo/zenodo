# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
WebSession templates which customizes the look and feel of
the user info box.
"""

from cgi import escape
from base64 import encodestring
from flask import render_template, url_for

from invenio.websession_templates import Template as DefaultTemplate
from invenio.config import CFG_OPENAIRE_PORTAL_URL, CFG_SITE_SECURE_URL, \
    CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS, CFG_SITE_LANG
from invenio.urlutils import create_url
from invenio.messages import gettext_set_language


class Template(DefaultTemplate):
    def tmpl_create_userinfobox(self, ln, url_referer, guest, username, submitter, referee, admin, usebaskets, usemessages, usealerts, usegroups, useloans, usestats):
        """
        Displays the user block.

        Generates a URL to login via OpenAIRE portal (robot login).

        Parameters:

          - 'ln' *string* - The language to display the interface in

          - 'url_referer' *string* - URL of the page being displayed

          - 'guest' *boolean* - If the user is guest

          - 'username' *string* - The username (nickname or email)

          - 'submitter' *boolean* - If the user is submitter

          - 'referee' *boolean* - If the user is referee

          - 'admin' *boolean* - If the user is admin

          - 'usebaskets' *boolean* - If baskets are enabled for the user

          - 'usemessages' *boolean* - If messages are enabled for the user

          - 'usealerts' *boolean* - If alerts are enabled for the user

          - 'usegroups' *boolean* - If groups are enabled for the user

          - 'useloans' *boolean* - If loans are enabled for the user

          - 'usestats' *boolean* - If stats are enabled for the user

        @note: with the update of CSS classes (cds.cds ->
            invenio.css), the variables useloans etc are not used in
            this function, since they are in the menus.  But we keep
            them in the function signature for backwards
            compatibility.
        """

        # load the right message language
        _ = gettext_set_language(ln)

        invenio_loginurl = url_referer or '%s/youraccount/display?ln=%s' % (CFG_SITE_SECURE_URL, ln)
        loginurl = create_url(CFG_OPENAIRE_PORTAL_URL, {"option": "com_openaire", "view": "login", "return": encodestring(invenio_loginurl)})
        invenio_logouturl = "%s/youraccount/logout?ln=%s" % (CFG_SITE_SECURE_URL, ln)
        logouturl = create_url(CFG_OPENAIRE_PORTAL_URL, {"option": "com_openaire", "view": "logout", "return": encodestring(invenio_logouturl)})

        out = """<img src="/img/user-icon-1-20x20.gif" border="0" alt=""/> """
        if guest:
            out += """%(guest_msg)s ::
                   <a class="userinfo" href="%(loginurl)s">%(login)s</a>""" % {
                     'loginurl': escape(loginurl, True),
                     'guest_msg' : escape(_("guest")),
                     'login' : escape(_('login'))
                   }
        else:
            out += """
               <a class="userinfo" href="%(sitesecureurl)s/youraccount/display?ln=%(ln)s">%(username)s</a> :: """ % {
                    'sitesecureurl' : escape(CFG_SITE_SECURE_URL, True),
                    'ln' : escape(ln, True),
                    'username' : escape(username)
               }
            out += """<a class="userinfo" href="%(logouturl)s">%(logout)s</a>""" % {
                    'logouturl': escape(logouturl, True),
                    'logout' : escape(_("logout")),
                }
        return out

    def tmpl_account_address_activation_email_body(
            self, email, address_activation_key, ip_address, ln=CFG_SITE_LANG):
        """
        The body of the email that sends email address activation cookie
        passwords to users.
        """
        from urllib import urlencode
        ctx = {
            "ip_address": ip_address,
            "email": email,
            "activation_link": "%s/youraccount/access?%s" % (
                CFG_SITE_SECURE_URL,
                urlencode({
                    "ln": ln,
                    "mailcookie": address_activation_key,
                })
            ),
            "days": CFG_WEBSESSION_ADDRESS_ACTIVATION_EXPIRE_IN_DAYS,
        }

        return render_template(
            "websession_account_address_activation_email_body.html",
            **ctx).encode('utf8')
