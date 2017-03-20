# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utils for communities."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_mail import Mail, Message

def render_template_to_string(template, context):
    """Render a template from the template folder with the given context.

    Code based on
    `<https://github.com/mitsuhiko/flask/blob/master/flask/templating.py>`_
    :param template: the string template, or name of the template to be
                     rendered, or an iterable with template names
                     the first one existing will be rendered.
    :param context: the variables that should be available in the
                    context of the template.
    :return: a string.
    """
    template = current_app.jinja_env.get_or_select_template(template)
    return template.render(context)

def format_request_email_title(context):
    """Format the email message title for contact form notification.

    :param context: Context parameters passed to formatter.
    :type context: dict.
    :returns: Email message title.
    :rtype: str
    """
    template = current_app.config['PAGES_EMAIL_TITLE_TEMPLATE'],
    return render_template_to_string(template, context)

def format_request_email_body(context):
    """Format the email message body for contact form notification.

    :param context: Context parameters passed to formatter.
    :type context: dict.
    :returns: Email message body.
    :rtype: str
    """
    template = current_app.config['PAGES_EMAIL_BODY_TEMPLATE'],
    return render_template_to_string(template, context)

def send_support_email(context):
    """Signal for sending emails after contact form validated."""
    msg_body = format_request_email_body(context)
    msg_title = format_request_email_title(context)

    mail = Mail(current_app)

    msg = Message(
        msg_title,
        sender=current_app.config['PAGES_SENDER_EMAIL'],
        recipients=current_app.config['PAGES_SUPPORT_EMAIL'],
        reply_to=context['form'].email.data,
        body=msg_body
    )

    if context['form'].attachments.data:
        msg.attach(context['form'].attachments.data.filename,
                   'application/octet-stream',
                   context['form'].attachments.data.read())

    mail.send(msg)
