# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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

"""Invenio ACCOUNT HANDLING"""

__revision__ = "$Id$"

__lastupdated__ = """$Date$"""

import cgi
from datetime import timedelta
import os

from invenio.config import \
     CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS, \
     CFG_ACCESS_CONTROL_LEVEL_SITE, \
     CFG_ACCESS_CONTROL_NOTIFY_USER_ABOUT_NEW_ACCOUNT, \
     CFG_SITE_NAME, \
     CFG_SITE_NAME_INTL, \
     CFG_SITE_SUPPORT_EMAIL, \
     CFG_SITE_SECURE_URL, \
     CFG_SITE_URL, \
     CFG_CERN_SITE, \
     CFG_WEBSESSION_RESET_PASSWORD_EXPIRE_IN_DAYS, \
     CFG_OPENAIRE_SITE
from invenio import webuser
from invenio.webpage import page
from invenio import webaccount
from invenio import webbasket
from invenio import webalert
from invenio.dbquery import run_sql
from invenio.webmessage import account_new_mail
from invenio.access_control_engine import acc_authorize_action
from invenio.webinterface_handler import wash_urlargd, WebInterfaceDirectory
from invenio.webinterface_handler_config import HTTP_BAD_REQUEST
from invenio.urlutils import redirect_to_url, make_canonical_urlargd
from invenio import webgroup
from invenio import webgroup_dblayer
from invenio.messages import gettext_set_language, wash_language
from invenio.mailutils import send_email
from invenio.access_control_mailcookie import mail_cookie_retrieve_kind, \
    mail_cookie_check_pw_reset, mail_cookie_delete_cookie, \
    mail_cookie_create_pw_reset, mail_cookie_check_role, \
    mail_cookie_check_mail_activation, InvenioWebAccessMailCookieError, \
    InvenioWebAccessMailCookieDeletedError, mail_cookie_check_authorize_action
from invenio.access_control_config import CFG_WEBACCESS_WARNING_MSGS, \
    CFG_EXTERNAL_AUTH_USING_SSO, CFG_EXTERNAL_AUTH_LOGOUT_SSO, \
    CFG_EXTERNAL_AUTHENTICATION

import invenio.template
websession_templates = invenio.template.load('websession')
bibcatalog_templates = invenio.template.load('bibcatalog')

class WebInterfaceYourAccountPages(WebInterfaceDirectory):

    _exports = ['', 'edit', 'change', 'lost', 'display',
                'send_email', 'youradminactivities', 'access',
                'delete', 'logout', 'login', 'register', 'resetpassword',
                'robotlogin', 'robotlogout']

    _force_https = True

    def index(self, req, form):
        redirect_to_url(req, '%s/youraccount/display' % CFG_SITE_SECURE_URL)

    def access(self, req, form):
        args = wash_urlargd(form, {'mailcookie' : (str, '')})
        _ = gettext_set_language(args['ln'])
        title = _("Mail Cookie Service")
        try:
            kind = mail_cookie_retrieve_kind(args['mailcookie'])
            if kind == 'pw_reset':
                redirect_to_url(req, '%s/youraccount/resetpassword?k=%s&ln=%s' % (CFG_SITE_SECURE_URL, args['mailcookie'], args['ln']))
            elif kind == 'role':
                uid = webuser.getUid(req)
                try:
                    (role_name, expiration) = mail_cookie_check_role(args['mailcookie'], uid)
                except InvenioWebAccessMailCookieDeletedError:
                    return page(title=_("Role authorization request"), req=req, body=_("This request for an authorization has already been authorized."), uid=webuser.getUid(req), navmenuid='youraccount', language=args['ln'], secure_page_p=1)
                return page(title=title,
                body=webaccount.perform_back(
                    _("You have successfully obtained an authorization as %(x_role)s! "
                    "This authorization will last until %(x_expiration)s and until "
                    "you close your browser if you are a guest user.") %
                    {'x_role' : '<strong>%s</strong>' % role_name,
                     'x_expiration' : '<em>%s</em>' % expiration.strftime("%Y-%m-%d %H:%M:%S")},
                    '/youraccount/display?ln=%s' % args['ln'], _('login'), args['ln']),
                req=req,
                uid=webuser.getUid(req),
                language=args['ln'],
                lastupdated=__lastupdated__,
                navmenuid='youraccount',
                secure_page_p=1)
            elif kind == 'mail_activation':
                try:
                    email = mail_cookie_check_mail_activation(args['mailcookie'])
                    if not email:
                        raise StandardError
                    webuser.confirm_email(email)
                    body = "<p>" + _("You have confirmed the validity of your email"
                        " address!") + "</p>"
                    if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS == 1:
                        body += "<p>" + _("Please, wait for the administrator to "
                            "enable your account.") + "</p>"
                    else:
                        uid = webuser.update_Uid(req, email)
                        body += "<p>" + _("You can now go to %(x_url_open)syour account page%(x_url_close)s.") % {'x_url_open' : '<a href="/youraccount/display?ln=%s">' % args['ln'], 'x_url_close' : '</a>'} + "</p>"
                    return page(title=_("Email address successfully activated"),
                    body=body, req=req, language=args['ln'], uid=webuser.getUid(req), lastupdated=__lastupdated__, navmenuid='youraccount', secure_page_p=1)
                except InvenioWebAccessMailCookieDeletedError, e:
                    body = "<p>" + _("You have already confirmed the validity of your email address!") + "</p>"
                    if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS == 1:
                        body += "<p>" + _("Please, wait for the administrator to "
                            "enable your account.") + "</p>"
                    else:
                        body += "<p>" + _("You can now go to %(x_url_open)syour account page%(x_url_close)s.") % {'x_url_open' : '<a href="/youraccount/display?ln=%s">' % args['ln'], 'x_url_close' : '</a>'} + "</p>"
                    return page(title=_("Email address successfully activated"),
                        body=body, req=req, language=args['ln'], uid=webuser.getUid(req), lastupdated=__lastupdated__, navmenuid='youraccount', secure_page_p=1)
                return webuser.page_not_authorized(req, "../youraccount/access",
                    text=_("This request for confirmation of an email "
                    "address is not valid or"
                    " is expired."), navmenuid='youraccount')
        except InvenioWebAccessMailCookieError:
            return webuser.page_not_authorized(req, "../youraccount/access",
                text=_("This request for an authorization is not valid or"
                " is expired."), navmenuid='youraccount')

    def resetpassword(self, req, form):
        args = wash_urlargd(form, {
            'k' : (str, ''),
            'reset' : (int, 0),
            'password' : (str, ''),
            'password2' : (str, '')
            })

        _ = gettext_set_language(args['ln'])

        title = _('Reset password')
        reset_key = args['k']

        try:
            email = mail_cookie_check_pw_reset(reset_key)
        except InvenioWebAccessMailCookieDeletedError:
            return page(title=title, req=req, body=_("This request for resetting a password has already been used."), uid=webuser.getUid(req), navmenuid='youraccount', language=args['ln'], secure_page_p=1)
        except InvenioWebAccessMailCookieError:
            return webuser.page_not_authorized(req, "../youraccount/access",
                text=_("This request for resetting a password is not valid or"
                " is expired."), navmenuid='youraccount')

        if email is None or CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS >= 3:
            return webuser.page_not_authorized(req, "../youraccount/resetpassword",
                    text=_("This request for resetting the password is not valid or"
                    " is expired."), navmenuid='youraccount')

        if not args['reset']:
            return page(title=title,
                    body=webaccount.perform_reset_password(args['ln'], email, reset_key),
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

        elif args['password'] != args['password2']:
            msg = _('The two provided passwords aren\'t equal.')
            return page(title=title,
                body=webaccount.perform_reset_password(args['ln'], email, reset_key, msg),
                req=req,
                secure_page_p = 1,
                language=args['ln'],
                lastupdated=__lastupdated__,
                navmenuid='youraccount')

        run_sql('UPDATE user SET password=AES_ENCRYPT(email,%s) WHERE email=%s', (args['password'], email))

        mail_cookie_delete_cookie(reset_key)

        return page(title=title,
            body=webaccount.perform_back(
                _("The password was successfully set! "
                "You can now proceed with the login."),
                '/youraccount/login?ln=%s' % args['ln'], _('login'), args['ln']),
            req=req,
            language=args['ln'],
            lastupdated=__lastupdated__,
            navmenuid='youraccount', secure_page_p=1)

    def display(self, req, form):
        args = wash_urlargd(form, {})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/display",
                                               navmenuid='youraccount')

        if webuser.isGuestUser(uid):
            return page(title=_("Your Account"),
                        body=webaccount.perform_info(req, args['ln']),
                        description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        uid=uid,
                        req=req,
                        secure_page_p = 1,
                        language=args['ln'],
                        lastupdated=__lastupdated__,
                        navmenuid='youraccount')

        username = webuser.get_nickname_or_email(uid)
        user_info = webuser.collect_user_info(req)
        bask = user_info['precached_usebaskets'] and webbasket.account_list_baskets(uid, ln=args['ln']) or ''
        aler = user_info['precached_usealerts'] and webalert.account_list_alerts(uid, ln=args['ln']) or ''
        sear = webalert.account_list_searches(uid, ln=args['ln'])
        msgs = user_info['precached_usemessages'] and account_new_mail(uid, ln=args['ln']) or ''
        grps = user_info['precached_usegroups'] and webgroup.account_group(uid, ln=args['ln']) or ''
        appr = user_info['precached_useapprove']
        sbms = user_info['precached_viewsubmissions']
        loan = ''
        admn = webaccount.perform_youradminactivities(user_info, args['ln'])
        return page(title=_("Your Account"),
                    body=webaccount.perform_display_account(req, username, bask, aler, sear, msgs, loan, grps, sbms, appr, admn, args['ln']),
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')


    def edit(self, req, form):
        args = wash_urlargd(form, {"verbose" : (int, 0)})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/edit",
                                               navmenuid='youraccount')

        if webuser.isGuestUser(uid):
            return webuser.page_not_authorized(req, "../youraccount/edit",
                                               text=_("This functionality is forbidden to guest users."),
                                               navmenuid='youraccount')
        body = ''

        user_info = webuser.collect_user_info(req)
        if args['verbose'] == 9:
            keys = user_info.keys()
            keys.sort()
            for key in keys:
                body += "<b>%s</b>:%s<br />" % (key, user_info[key])

        #check if the user should see bibcatalog user name / passwd in the settings
        can_config_bibcatalog = (acc_authorize_action(user_info, 'runbibedit')[0] == 0)
        return page(title= _("Your Settings"),
                    body=body+webaccount.perform_set(webuser.get_email(uid),
                                                     args['ln'], can_config_bibcatalog,
                                                     verbose=args['verbose']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description=_("%s Personalize, Your Settings")  % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

    def change(self, req, form):
        args = wash_urlargd(form, {
            'nickname': (str, None),
            'email': (str, None),
            'old_password': (str, None),
            'password': (str, None),
            'password2': (str, None),
            'login_method': (str, ""),
            'group_records' : (int, None),
            'latestbox' : (int, None),
            'helpbox' : (int, None),
            'lang' : (str, None),
            'bibcatalog_username' : (str, None),
            'bibcatalog_password' : (str, None),
            })

        ## Wash arguments:
        args['login_method'] = wash_login_method(args['login_method'])
        if args['email']:
            args['email'] = args['email'].lower()

        ## Load the right message language:
        _ = gettext_set_language(args['ln'])

        ## Identify user and load old preferences:
        uid = webuser.getUid(req)
        prefs = webuser.get_user_preferences(uid)

        ## Check rights:
        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/change",
                                               navmenuid='youraccount')

        # FIXME: the branching below is far from optimal.  Should be
        # based on the submitted form name ids, to know precisely on
        # which form the user clicked.  Not on the passed values, as
        # is the case now.  The function body is too big and in bad
        # need of refactoring anyway.

        ## Will hold the output messages:
        mess = ''

        ## Change login method if needed:
        if args['login_method'] and CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS < 4 \
                and args['login_method'] in CFG_EXTERNAL_AUTHENTICATION:
            title = _("Settings edited")
            act = "/youraccount/display?ln=%s" % args['ln']
            linkname = _("Show account")

            if prefs['login_method'] != args['login_method']:
                if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS >= 4:
                    mess += '<p>' + _("Unable to change login method.")
                elif not CFG_EXTERNAL_AUTHENTICATION[args['login_method']]:
                    # Switching to internal authentication: we drop any external datas
                    p_email = webuser.get_email(uid)
                    webuser.drop_external_settings(uid)
                    webgroup_dblayer.drop_external_groups(uid)
                    prefs['login_method'] = args['login_method']
                    webuser.set_user_preferences(uid, prefs)
                    mess += "<p>" + _("Switched to internal login method.") + " "
                    mess += _("Please note that if this is the first time that you are using this account "
                              "with the internal login method then the system has set for you "
                              "a randomly generated password. Please click the "
                              "following button to obtain a password reset request "
                              "link sent to you via email:") + '</p>'
                    mess += """<p><form  method="post" action="../youraccount/send_email">
                        <input type="hidden" name="p_email" value="%s">
                        <input class="formbutton" type="submit" value="%s">
                        </form></p>""" % (p_email, _("Send Password"))
                else:
                    query = """SELECT email FROM user
                            WHERE id = %i"""
                    res = run_sql(query % uid)
                    if res:
                        email = res[0][0]
                    else:
                        email = None
                    if not email:
                        mess += '<p>' + _("Unable to switch to external login method %s, because your email address is unknown.") % cgi.escape(args['login_method'])
                    else:
                        try:
                            if not CFG_EXTERNAL_AUTHENTICATION[args['login_method']].user_exists(email):
                                mess += '<p>' +  _("Unable to switch to external login method %s, because your email address is unknown to the external login system.") % cgi.escape(args['login_method'])
                            else:
                                prefs['login_method'] = args['login_method']
                                webuser.set_user_preferences(uid, prefs)
                                mess += '<p>' + _("Login method successfully selected.")
                        except AttributeError:
                            mess += '<p>' + _("The external login method %s does not support email address based logins.  Please contact the site administrators.") % cgi.escape(args['login_method'])

        ## Change email or nickname:
        if args['email'] or args['nickname']:
            uid2 = webuser.emailUnique(args['email'])
            uid_with_the_same_nickname = webuser.nicknameUnique(args['nickname'])
            if (CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS >= 2 or (CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS <= 1 and \
                                                           webuser.email_valid_p(args['email']))) \
               and (args['nickname'] is None or webuser.nickname_valid_p(args['nickname'])) \
               and uid2 != -1 and (uid2 == uid or uid2 == 0) \
               and uid_with_the_same_nickname != -1 and (uid_with_the_same_nickname == uid or uid_with_the_same_nickname == 0):
                if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS < 3:
                    change = webuser.updateDataUser(uid,
                                                    args['email'],
                                                    args['nickname'])
                else:
                    return webuser.page_not_authorized(req, "../youraccount/change",
                                                       navmenuid='youraccount')
                if change:
                    mess += '<p>' + _("Settings successfully edited.")
                    mess += '<p>' + _("Note that if you have changed your email address, "
                                      "you will have to %(x_url_open)sreset your password%(x_url_close)s anew.") % \
                                      {'x_url_open': '<a href="%s">' % (CFG_SITE_SECURE_URL + '/youraccount/lost?ln=%s' % args['ln']),
                                       'x_url_close': '</a>'}
                act = "/youraccount/display?ln=%s" % args['ln']
                linkname = _("Show account")
                title = _("Settings edited")
            elif args['nickname'] is not None and not webuser.nickname_valid_p(args['nickname']):
                mess += '<p>' + _("Desired nickname %s is invalid.") % cgi.escape(args['nickname'])
                mess += " " + _("Please try again.")
                act = "/youraccount/edit?ln=%s" % args['ln']
                linkname = _("Edit settings")
                title = _("Editing settings failed")
            elif not webuser.email_valid_p(args['email']):
                mess += '<p>' + _("Supplied email address %s is invalid.") % cgi.escape(args['email'])
                mess += " " + _("Please try again.")
                act = "/youraccount/edit?ln=%s" % args['ln']
                linkname = _("Edit settings")
                title = _("Editing settings failed")
            elif uid2 == -1 or uid2 != uid and not uid2 == 0:
                mess += '<p>' + _("Supplied email address %s already exists in the database.") % cgi.escape(args['email'])
                mess += " " + websession_templates.tmpl_lost_your_password_teaser(args['ln'])
                mess += " " + _("Or please try again.")
                act = "/youraccount/edit?ln=%s" % args['ln']
                linkname = _("Edit settings")
                title = _("Editing settings failed")
            elif uid_with_the_same_nickname == -1 or uid_with_the_same_nickname != uid and not uid_with_the_same_nickname == 0:
                mess += '<p>' + _("Desired nickname %s is already in use.") % cgi.escape(args['nickname'])
                mess += " " + _("Please try again.")
                act = "/youraccount/edit?ln=%s" % args['ln']
                linkname = _("Edit settings")
                title = _("Editing settings failed")

        ## Change passwords:
        if args['old_password'] or args['password'] or args['password2']:
            if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS >= 3:
                mess += '<p>' + _("Users cannot edit passwords on this site.")
            else:
                res = run_sql("SELECT id FROM user "
                    "WHERE AES_ENCRYPT(email,%s)=password AND id=%s",
                    (args['old_password'], uid))
                if res:
                    if args['password'] == args['password2']:
                        webuser.updatePasswordUser(uid, args['password'])
                        mess += '<p>' + _("Password successfully edited.")
                        act = "/youraccount/display?ln=%s" % args['ln']
                        linkname = _("Show account")
                        title = _("Password edited")
                    else:
                        mess += '<p>' + _("Both passwords must match.")
                        mess += " " + _("Please try again.")
                        act = "/youraccount/edit?ln=%s" % args['ln']
                        linkname = _("Edit settings")
                        title = _("Editing password failed")
                else:
                    mess += '<p>' + _("Wrong old password inserted.")
                    mess += " " + _("Please try again.")
                    act = "/youraccount/edit?ln=%s" % args['ln']
                    linkname = _("Edit settings")
                    title = _("Editing password failed")

        ## Change search-related settings:
        if args['group_records']:
            prefs = webuser.get_user_preferences(uid)
            prefs['websearch_group_records'] = args['group_records']
            prefs['websearch_latestbox'] = args['latestbox']
            prefs['websearch_helpbox'] = args['helpbox']
            webuser.set_user_preferences(uid, prefs)
            title = _("Settings edited")
            act = "/youraccount/display?ln=%s" % args['ln']
            linkname = _("Show account")
            mess += '<p>' + _("User settings saved correctly.")

        ## Change language-related settings:
        if args['lang']:
            lang = wash_language(args['lang'])
            prefs = webuser.get_user_preferences(uid)
            prefs['language'] = lang
            args['ln'] = lang
            _ = gettext_set_language(lang)
            webuser.set_user_preferences(uid, prefs)
            title = _("Settings edited")
            act = "/youraccount/display?ln=%s" % args['ln']
            linkname = _("Show account")
            mess += '<p>' + _("User settings saved correctly.")

        ## Edit cataloging-related settings:
        if args['bibcatalog_username'] or args['bibcatalog_password']:
            act = "/youraccount/display?ln=%s" % args['ln']
            linkname = _("Show account")
            if ((len(args['bibcatalog_username']) == 0) or (len(args['bibcatalog_password']) == 0)):
                title = _("Editing bibcatalog authorization failed")
                mess += '<p>' + _("Empty username or password")
            else:
                title = _("Settings edited")
                prefs['bibcatalog_username'] = args['bibcatalog_username']
                prefs['bibcatalog_password'] = args['bibcatalog_password']
                webuser.set_user_preferences(uid, prefs)
                mess += '<p>' + _("User settings saved correctly.")

        if not mess:
            mess = _("Unable to update settings.")
        if not act:
            act = "/youraccount/edit?ln=%s" % args['ln']
        if not linkname:
            linkname = _("Edit settings")
        if not title:
            title = _("Editing settings failed")

        ## Finally, output the results:
        return page(title=title,
                    body=webaccount.perform_back(mess, act, linkname, args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

    def lost(self, req, form):
        args = wash_urlargd(form, {})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/lost",
                                               navmenuid='youraccount')

        return page(title=_("Lost your password?"),
                    body=webaccount.perform_lost(args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')


    def send_email(self, req, form):
        # set all the declared query fields as local variables
        args = wash_urlargd(form, {'p_email': (str, None)})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/send_email",
                                               navmenuid='youraccount')

        user_prefs = webuser.get_user_preferences(webuser.emailUnique(args['p_email']))
        if user_prefs:
            if user_prefs['login_method'] in CFG_EXTERNAL_AUTHENTICATION and \
               CFG_EXTERNAL_AUTHENTICATION[user_prefs['login_method']] is not None:
                eMsg = _("Cannot send password reset request since you are using external authentication system.")
                return page(title=_("Your Account"),
                            body=webaccount.perform_emailMessage(eMsg, args['ln']),
                            description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                            keywords=_("%s, personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME)),
                            uid=uid, req=req,
                            secure_page_p = 1,
                            language=args['ln'],
                            lastupdated=__lastupdated__,
                            navmenuid='youraccount')

        try:
            reset_key = mail_cookie_create_pw_reset(args['p_email'], cookie_timeout=timedelta(days=CFG_WEBSESSION_RESET_PASSWORD_EXPIRE_IN_DAYS))
        except InvenioWebAccessMailCookieError:
            reset_key = None
        if reset_key is None:
            eMsg = _("The entered email address does not exist in the database.")
            return page(title=_("Your Account"),
                        body=webaccount.perform_emailMessage(eMsg, args['ln']),
                        description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        uid=uid, req=req,
                        secure_page_p = 1,
                        language=args['ln'],
                        lastupdated=__lastupdated__,
                        navmenuid='youraccount')

        ip_address = req.remote_host or req.remote_ip

        if not send_email(CFG_SITE_SUPPORT_EMAIL, args['p_email'], "%s %s"
                % (_("Password reset request for"),
                CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME)),
                websession_templates.tmpl_account_reset_password_email_body(
                    args['p_email'],reset_key, ip_address, args['ln'])):
            eMsg = _("The entered email address is incorrect, please check that it is written correctly (e.g. johndoe@example.com).")
            return page(title=_("Incorrect email address"),
                        body=webaccount.perform_emailMessage(eMsg, args['ln']),
                        description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        uid=uid,
                        req=req,
                        secure_page_p = 1,
                        language=args['ln'],
                        lastupdated=__lastupdated__,
                        navmenuid='youraccount')
        return page(title=_("Reset password link sent"),
                    body=webaccount.perform_emailSent(args['p_email'], args['ln']),
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid, req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

    def youradminactivities(self, req, form):
        args = wash_urlargd(form, {})
        uid = webuser.getUid(req)
        user_info = webuser.collect_user_info(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/youradminactivities",
                                               navmenuid='admin')

        return page(title=_("Your Administrative Activities"),
                    body=webaccount.perform_youradminactivities(user_info, args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='admin')

    def delete(self, req, form):
        args = wash_urlargd(form, {})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/delete",
                                               navmenuid='youraccount')

        return page(title=_("Delete Account"),
                    body=webaccount.perform_delete(args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

    def logout(self, req, form):
        args = wash_urlargd(form, {})
        uid = webuser.logoutUser(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if uid == -1 or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../youraccount/logout",
                                               navmenuid='youraccount')

        if CFG_EXTERNAL_AUTH_USING_SSO:
            return redirect_to_url(req, CFG_EXTERNAL_AUTH_LOGOUT_SSO)

        return page(title=_("Logout"),
                    body=webaccount.perform_logout(req, args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords=_("%s, personalize") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')

    def robotlogout(self, req, form):
        """
        Implement logout method for external service providers.
        """
        webuser.logoutUser(req)
        if CFG_OPENAIRE_SITE:
            from invenio.config import CFG_OPENAIRE_PORTAL_URL
            redirect_to_url(req, CFG_OPENAIRE_PORTAL_URL)
        else:
            redirect_to_url(req, "%s/img/pix.png" % CFG_SITE_URL)

    def robotlogin(self, req, form):
        """
        Implement authentication method for external service providers.
        """
        from invenio.external_authentication import InvenioWebAccessExternalAuthError
        args = wash_urlargd(form, {
            'login_method': (str, None),
            'remember_me' : (str, ''),
            'referer': (str, ''),
            'p_un': (str, ''),
            'p_pw': (str, '')
        })
        # sanity checks:
        args['login_method'] = wash_login_method(args['login_method'])
        args['remember_me'] = args['remember_me'] != ''
        locals().update(args)
        if CFG_ACCESS_CONTROL_LEVEL_SITE > 0:
            return webuser.page_not_authorized(req, "../youraccount/login?ln=%s" % args['ln'],
                                               navmenuid='youraccount')
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        try:
            (iden, args['p_un'], args['p_pw'], msgcode) = webuser.loginUser(req, args['p_un'], args['p_pw'], args['login_method'])
        except InvenioWebAccessExternalAuthError, err:
            return page("Error", body=str(err))
        if len(iden)>0:
            uid = webuser.update_Uid(req, args['p_un'], args['remember_me'])
            uid2 = webuser.getUid(req)
            if uid2 == -1:
                webuser.logoutUser(req)
                return webuser.page_not_authorized(req, "../youraccount/login?ln=%s" % args['ln'], uid=uid,
                                                    navmenuid='youraccount')

            # login successful!
            if args['referer']:
                ## HACK for OpenAIRE
                if args['referer'].startswith('https://openaire.cern.ch/deposit'):
                    args['referer'] = args['referer'].replace('https://openaire.cern.ch/deposit', 'http://openaire.cern.ch/deposit')
                redirect_to_url(req, args['referer'])
            else:
                return self.display(req, form)
        else:
            mess = CFG_WEBACCESS_WARNING_MSGS[msgcode] % cgi.escape(args['login_method'])
            if msgcode == 14:
                if webuser.username_exists_p(args['p_un']):
                    mess = CFG_WEBACCESS_WARNING_MSGS[15] % cgi.escape(args['login_method'])
            act = '/youraccount/login%s' % make_canonical_urlargd({'ln' : args['ln'], 'referer' : args['referer']}, {})
            return page(title=_("Login"),
                        body=webaccount.perform_back(mess, act, _("login"), args['ln']),
                        navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                        description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        keywords="%s , personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        uid=uid,
                        req=req,
                        secure_page_p = 1,
                        language=args['ln'],
                        lastupdated=__lastupdated__,
                        navmenuid='youraccount')



    def login(self, req, form):
        args = wash_urlargd(form, {
            'p_un': (str, None),
            'p_pw': (str, None),
            'login_method': (str, None),
            'action': (str, ''),
            'remember_me' : (str, ''),
            'referer': (str, '')})

        if CFG_OPENAIRE_SITE:
            from invenio.config import CFG_OPENAIRE_PORTAL_URL
            if CFG_OPENAIRE_PORTAL_URL:
                from invenio.urlutils import create_url
                from base64 import encodestring
                invenio_loginurl = args['referer'] or '%s/youraccount/display?ln=%s' % (CFG_SITE_SECURE_URL, args['ln'])
                loginurl = create_url(CFG_OPENAIRE_PORTAL_URL, {"option": "com_openaire", "view": "login", "return": encodestring(invenio_loginurl)})
                redirect_to_url(req, loginurl)

        # sanity checks:
        args['login_method'] = wash_login_method(args['login_method'])
        if args['p_un']:
            args['p_un'] = args['p_un'].strip()
        args['remember_me'] = args['remember_me'] != ''

        locals().update(args)

        if CFG_ACCESS_CONTROL_LEVEL_SITE > 0:
            return webuser.page_not_authorized(req, "../youraccount/login?ln=%s" % args['ln'],
                                               navmenuid='youraccount')

        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if args['action']:
            cookie = args['action']
            try:
                action, arguments = mail_cookie_check_authorize_action(cookie)
            except InvenioWebAccessMailCookieError:
                pass

        if not CFG_EXTERNAL_AUTH_USING_SSO:
            if args['p_un'] is None or not args['login_method']:
                return page(title=_("Login"),
                            body=webaccount.create_login_page_box(args['referer'], args['ln']),
                            navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                            description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                            keywords="%s , personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                            uid=uid,
                            req=req,
                            secure_page_p=1,
                            language=args['ln'],
                            lastupdated=__lastupdated__,
                            navmenuid='youraccount')
            (iden, args['p_un'], args['p_pw'], msgcode) = webuser.loginUser(req, args['p_un'], args['p_pw'], args['login_method'])
        else:
            # Fake parameters for p_un & p_pw because SSO takes them from the environment
            (iden, args['p_un'], args['p_pw'], msgcode) = webuser.loginUser(req, '', '', CFG_EXTERNAL_AUTH_USING_SSO)
            args['remember_me'] = False
        if len(iden)>0:
            uid = webuser.update_Uid(req, args['p_un'], args['remember_me'])
            uid2 = webuser.getUid(req)
            if uid2 == -1:
                webuser.logoutUser(req)
                return webuser.page_not_authorized(req, "../youraccount/login?ln=%s" % args['ln'], uid=uid,
                                                    navmenuid='youraccount')

            # login successful!
            if args['referer']:
                redirect_to_url(req, args['referer'])
            else:
                return self.display(req, form)
        else:
            mess = CFG_WEBACCESS_WARNING_MSGS[msgcode] % cgi.escape(args['login_method'])
            if msgcode == 14:
                if webuser.username_exists_p(args['p_un']):
                    mess = CFG_WEBACCESS_WARNING_MSGS[15] % cgi.escape(args['login_method'])
            act = '/youraccount/login%s' % make_canonical_urlargd({'ln' : args['ln'], 'referer' : args['referer']}, {})
            return page(title=_("Login"),
                        body=webaccount.perform_back(mess, act, _("login"), args['ln']),
                        navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                        description="%s Personalize, Main page" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        keywords="%s , personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                        uid=uid,
                        req=req,
                        secure_page_p = 1,
                        language=args['ln'],
                        lastupdated=__lastupdated__,
                        navmenuid='youraccount')

    def register(self, req, form):
        args = wash_urlargd(form, {
            'p_nickname': (str, None),
            'p_email': (str, None),
            'p_pw': (str, None),
            'p_pw2': (str, None),
            'action': (str, "login"),
            'referer': (str, "")})

        if CFG_ACCESS_CONTROL_LEVEL_SITE > 0:
            return webuser.page_not_authorized(req, "../youraccount/register?ln=%s" % args['ln'],
                                               navmenuid='youraccount')

        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(args['ln'])

        if args['p_nickname'] is None or args['p_email'] is None:
            return  page(title=_("Register"),
                         body=webaccount.create_register_page_box(args['referer'], args['ln']),
                         navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                         description=_("%s  Personalize, Main page") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                         keywords="%s , personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                         uid=uid,
                         req=req,
                         secure_page_p = 1,
                         language=args['ln'],
                         lastupdated=__lastupdated__,
                         navmenuid='youraccount')

        mess = ""
        act = ""
        if args['p_pw'] == args['p_pw2']:
            ruid = webuser.registerUser(req, args['p_email'], args['p_pw'],
                                        args['p_nickname'], ln=args['ln'])
        else:
            ruid = -2
        if ruid == 0:
            mess = _("Your account has been successfully created.")
            title = _("Account created")
            if CFG_ACCESS_CONTROL_NOTIFY_USER_ABOUT_NEW_ACCOUNT == 1:
                mess += " " + _("In order to confirm its validity, an email message containing an account activation key has been sent to the given email address.")
                mess += " " + _("Please follow instructions presented there in order to complete the account registration process.")
            if CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS >= 1:
                mess += " " + _("A second email will be sent when the account has been activated and can be used.")
            elif CFG_ACCESS_CONTROL_NOTIFY_USER_ABOUT_NEW_ACCOUNT != 1:
                uid = webuser.update_Uid(req, args['p_email'])
                mess += " " + _("You can now access your %(x_url_open)saccount%(x_url_close)s.") %\
                    {'x_url_open': '<a href="' + CFG_SITE_SECURE_URL + '/youraccount/display?ln=' + args['ln'] + '">',
                     'x_url_close': '</a>'}
        elif ruid == -2:
            mess = _("Both passwords must match.")
            mess += " " + _("Please try again.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 1:
            mess = _("Supplied email address %s is invalid.") % cgi.escape(args['p_email'])
            mess += " " + _("Please try again.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 2:
            mess = _("Desired nickname %s is invalid.") % cgi.escape(args['p_nickname'])
            mess += " " + _("Please try again.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 3:
            mess = _("Supplied email address %s already exists in the database.") % cgi.escape(args['p_email'])
            mess += " " + websession_templates.tmpl_lost_your_password_teaser(args['ln'])
            mess += " " + _("Or please try again.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 4:
            mess = _("Desired nickname %s already exists in the database.") % cgi.escape(args['p_nickname'])
            mess += " " + _("Please try again.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 5:
            mess = _("Users cannot register themselves, only admin can register them.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        elif ruid == 6:
            mess = _("The site is having troubles in sending you an email for confirming your email address.") + _("The error has been logged and will be taken in consideration as soon as possible.")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")
        else:
            # this should never happen
            mess = _("Internal Error")
            act = "/youraccount/register?ln=%s" % args['ln']
            title = _("Registration failure")

        return page(title=title,
                    body=webaccount.perform_back(mess,act, _("register"), args['ln']),
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, args['ln']) + _("Your Account") + """</a>""",
                    description=_("%s  Personalize, Main page") % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    keywords="%s , personalize" % CFG_SITE_NAME_INTL.get(args['ln'], CFG_SITE_NAME),
                    uid=uid,
                    req=req,
                    secure_page_p = 1,
                    language=args['ln'],
                    lastupdated=__lastupdated__,
                    navmenuid='youraccount')


class WebInterfaceYourTicketsPages(WebInterfaceDirectory):
    #support for /yourtickets url
    _exports = ['', 'display']

    def __call__(self, req, form):
        #if there is no trailing slash
        self.index(req, form)

    def index(self, req, form):
        #take all the parameters..
        unparsed_uri = req.unparsed_uri
        qstr = ""
        if unparsed_uri.count('?') > 0:
            dummy, qstr = unparsed_uri.split('?')
            qstr = '?'+qstr
        redirect_to_url(req, '/yourtickets/display'+qstr)

    def display(self, req, form):
        #show tickets for this user
        argd = wash_urlargd(form, {'ln': (str, ''), 'start': (int, 1) })
        uid = webuser.getUid(req)
        ln = argd['ln']
        start = argd['start']
        _ = gettext_set_language(ln)
        body = bibcatalog_templates.tmpl_your_tickets(uid, ln, start)
        return page(title=_("Your tickets"),
                    body=body,
                    navtrail="""<a class="navtrail" href="%s/youraccount/display?ln=%s">""" % (CFG_SITE_SECURE_URL, argd['ln']) + _("Your Account") + """</a>""",
                    uid=uid,
                    req=req,
                    language=argd['ln'],
                    lastupdated=__lastupdated__,
                    secure_page_p=1)

class WebInterfaceYourGroupsPages(WebInterfaceDirectory):

    _exports = ['', 'display', 'create', 'join', 'leave', 'edit', 'members']

    def index(self, req, form):
        redirect_to_url(req, '/yourgroups/display')

    def display(self, req, form):
        """
        Displays groups the user is admin of
        and the groups the user is member of(but not admin)
        @param ln:  language
        @return: the page for all the groups
        """
        argd = wash_urlargd(form, {})
        uid = webuser.getUid(req)

        # load the right message language
        _ = gettext_set_language(argd['ln'])

        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/display",
                                               navmenuid='yourgroups')

        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        body = webgroup.perform_request_groups_display(uid=uid,
                                                       ln=argd['ln'])

        return page(title         = _("Your Groups"),
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln']),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)

    def create(self, req, form):
        """create(): interface for creating a new group
        @param group_name: : name of the new webgroup.Must be filled
        @param group_description: : description of the new webgroup.(optionnal)
        @param join_policy: : join policy of the new webgroup.Must be chosen
        @param *button: which button was pressed
        @param ln: language
        @return: the compose page Create group
        """

        argd = wash_urlargd(form, {'group_name': (str, ""),
                                   'group_description': (str, ""),
                                   'join_policy': (str, ""),
                                   'create_button':(str, ""),
                                   'cancel':(str, "")
                                   })
        uid = webuser.getUid(req)
        # load the right message language
        _ = gettext_set_language(argd['ln'])

        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/create",
                                               navmenuid='yourgroups')
        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        if argd['cancel']:
            url = CFG_SITE_URL + '/yourgroups/display?ln=%s'
            url %= argd['ln']
            redirect_to_url(req, url)

        if argd['create_button'] :
            body= webgroup.perform_request_create_group(uid=uid,
                                                        group_name=argd['group_name'],
                                                        group_description=argd['group_description'],
                                                        join_policy=argd['join_policy'],
                                                        ln = argd['ln'])


        else:
            body = webgroup.perform_request_input_create_group(group_name=argd['group_name'],
                                                               group_description=argd['group_description'],
                                                               join_policy=argd['join_policy'],
                                                               ln=argd['ln'])
        title = _("Create new group")


        return page(title         = title,
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln'], title),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)

    def join(self, req, form):
        """join(): interface for joining a new group
        @param grpID: : list of the group the user wants to become a member.
        The user must select only one group.
        @param group_name: :  will search for groups matching group_name
        @param *button: which button was pressed
        @param ln: language
        @return: the compose page Join group
        """

        argd = wash_urlargd(form, {'grpID':(list, []),
                                   'group_name':(str, ""),
                                   'find_button':(str, ""),
                                   'join_button':(str, ""),
                                   'cancel':(str, "")
                                   })
        uid = webuser.getUid(req)
        # load the right message language
        _ = gettext_set_language(argd['ln'])

        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/join",
                                               navmenuid='yourgroups')
        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        if argd['cancel']:
            url = CFG_SITE_URL + '/yourgroups/display?ln=%s'
            url %= argd['ln']
            redirect_to_url(req, url)

        if argd['join_button']:
            search = 0
            if argd['group_name']:
                search = 1
            body = webgroup.perform_request_join_group(uid,
                                                       argd['grpID'],
                                                       argd['group_name'],
                                                       search,
                                                       argd['ln'])
        else:
            search = 0
            if argd['find_button']:
                search = 1
            body = webgroup.perform_request_input_join_group(uid,
                                                             argd['group_name'],
                                                             search,
                                                             ln=argd['ln'])

        title = _("Join New Group")
        return page(title         = title,
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln'], title),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)

    def leave(self, req, form):
        """leave(): interface for leaving a group
        @param grpID: : group the user wants to leave.
        @param group_name: :  name of the group the user wants to leave
        @param *button: which button was pressed
        @param confirmed: : the user is first asked to confirm
        @param ln: language
        @return: the compose page Leave group
        """

        argd = wash_urlargd(form, {'grpID':(int, 0),
                                   'group_name':(str, ""),
                                   'leave_button':(str, ""),
                                   'cancel':(str, ""),
                                   'confirmed': (int, 0)
                                   })
        uid = webuser.getUid(req)
        # load the right message language
        _ = gettext_set_language(argd['ln'])

        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/leave",
                                               navmenuid='yourgroups')
        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        if argd['cancel']:
            url = CFG_SITE_URL + '/yourgroups/display?ln=%s'
            url %= argd['ln']
            redirect_to_url(req, url)

        if argd['leave_button']:
            body = webgroup.perform_request_leave_group(uid,
                                                        argd['grpID'],
                                                        argd['confirmed'],
                                                        argd['ln'])
        else:
            body = webgroup.perform_request_input_leave_group(uid=uid,
                                                              ln=argd['ln'])
        title = _("Leave Group")
        return page(title         = title,
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln'], title),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)

    def edit(self, req, form):
        """edit(): interface for editing group
        @param grpID: : group ID
        @param group_name: : name of the new webgroup.Must be filled
        @param group_description: : description of the new webgroup.(optionnal)
        @param join_policy: : join policy of the new webgroup.Must be chosen
        @param update: button update group pressed
        @param delete: button delete group pressed
        @param cancel: button cancel pressed
        @param confirmed: : the user is first asked to confirm before deleting
        @param ln: language
        @return: the main page displaying all the groups
        """
        argd = wash_urlargd(form, {'grpID': (int, 0),
                                   'update': (str, ""),
                                   'cancel': (str, ""),
                                   'delete': (str, ""),
                                   'group_name': (str, ""),
                                   'group_description': (str, ""),
                                   'join_policy': (str, ""),
                                   'confirmed': (int, 0)
                                   })
        uid = webuser.getUid(req)
        # load the right message language
        _ = gettext_set_language(argd['ln'])
        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/display",
                                               navmenuid='yourgroups')
        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        if argd['cancel']:
            url = CFG_SITE_URL + '/yourgroups/display?ln=%s'
            url %= argd['ln']
            redirect_to_url(req, url)

        elif argd['delete']:
            body = webgroup.perform_request_delete_group(uid=uid,
                                                         grpID=argd['grpID'],
                                                         confirmed=argd['confirmed'])

        elif argd['update']:

            body = webgroup.perform_request_update_group(uid= uid,
                                                                             grpID=argd['grpID'],
                                                                             group_name=argd['group_name'],
                                                                             group_description=argd['group_description'],
                                                                             join_policy=argd['join_policy'],
                                                                             ln=argd['ln'])

        else :
            body= webgroup.perform_request_edit_group(uid=uid,
                                                      grpID=argd['grpID'],
                                                      ln=argd['ln'])



        title = _("Edit Group")
        return page(title = title,
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln'], title),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)


    def members(self, req, form):
        """member(): interface for managing members of a group
        @param grpID: : group ID
        @param add_member: button add_member pressed
        @param remove_member: button remove_member pressed
        @param reject_member: button reject__member pressed
        @param delete: button delete group pressed
        @param member_id: : ID of the existing member selected
        @param pending_member_id: : ID of the pending member selected
        @param cancel: button cancel pressed
        @param info: : info about last user action
        @param ln: language
        @return: the same page with data updated
        """
        argd = wash_urlargd(form, {'grpID': (int, 0),
                                   'cancel': (str, ""),
                                   'add_member': (str, ""),
                                   'remove_member': (str, ""),
                                   'reject_member': (str, ""),
                                   'member_id': (int, 0),
                                   'pending_member_id': (int, 0)
                                   })
        uid = webuser.getUid(req)
        # load the right message language
        _ = gettext_set_language(argd['ln'])
        if uid == -1 or webuser.isGuestUser(uid) or CFG_ACCESS_CONTROL_LEVEL_SITE >= 1:
            return webuser.page_not_authorized(req, "../yourgroups/display",
                                               navmenuid='yourgroups')
        user_info = webuser.collect_user_info(req)
        if not user_info['precached_usegroups']:
            return webuser.page_not_authorized(req, "../", \
                                       text = _("You are not authorized to use groups."))

        if argd['cancel']:
            url = CFG_SITE_URL + '/yourgroups/display?ln=%s'
            url %= argd['ln']
            redirect_to_url(req, url)

        if argd['remove_member']:
            body = webgroup.perform_request_remove_member(uid=uid,
                                                          grpID=argd['grpID'],
                                                          member_id=argd['member_id'],
                                                          ln=argd['ln'])

        elif argd['reject_member']:
            body = webgroup.perform_request_reject_member(uid=uid,
                                                          grpID=argd['grpID'],
                                                          user_id=argd['pending_member_id'],
                                                          ln=argd['ln'])

        elif argd['add_member']:
            body = webgroup.perform_request_add_member(uid=uid,
                                                       grpID=argd['grpID'],
                                                       user_id=argd['pending_member_id'],
                                                       ln=argd['ln'])

        else:
            body= webgroup.perform_request_manage_member(uid=uid,
                                                         grpID=argd['grpID'],
                                                         ln=argd['ln'])
        title = _("Edit group members")
        return page(title         = title,
                    body          = body,
                    navtrail      = webgroup.get_navtrail(argd['ln'], title),
                    uid           = uid,
                    req           = req,
                    language      = argd['ln'],
                    lastupdated   = __lastupdated__,
                    navmenuid     = 'yourgroups',
                    secure_page_p = 1)


def wash_login_method(login_method):
    """
    Wash the login_method parameter that came from the web input form.

    @param login_method: Wanted login_method value as it came from the
        web input form.
    @type login_method: string

    @return: Washed version of login_method.  If the login_method
        value is valid, then return it.  If it is not valid, then
        return `Local' (the default login method).
    @rtype: string

    @warning: Beware, 'Local' is hardcoded here!
    """
    if login_method in CFG_EXTERNAL_AUTHENTICATION:
        return login_method
    else:
        return 'Local'
