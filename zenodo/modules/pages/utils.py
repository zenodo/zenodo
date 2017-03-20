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

"""Utils for Zenodo Pages."""

from __future__ import absolute_import, print_function

from flask import current_app, request
from flask_mail import Message
from ua_parser import user_agent_parser


def render_template_to_string(template, context):
    """Render a template from the template folder with the given context.

    Code based on
    `<https://github.com/mitsuhiko/flask/blob/master/flask/templating.py>`_
    :param template: the string template, or name of the template to be
                     rendered, or an iterable with template names
                     the first one existing will be rendered.
    :param context: the variables that should be available in the
                    context of the template.
    :returns: A template string.
    :rtype: str
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
    template = current_app.config['PAGES_EMAIL_TITLE_TEMPLATE']
    return render_template_to_string(template, context)


def format_request_email_body(context):
    """Format the email message body for contact form notification.

    :param context: Context parameters passed to formatter.
    :type context: dict.
    :returns: Email message body.
    :rtype: str
    """
    template = current_app.config['PAGES_EMAIL_BODY_TEMPLATE']
    return render_template_to_string(template, context)


def check_attachment_size(attachments):
    """Function to check size of attachment within limits.

    :param attachments: Attachments files.
    :returns: True if the attachments size is acceptable.
    :rtype: bool
    """
    if len(attachments) == 0:
        return False
    if request.content_length:
        file_size = int(request.content_length)
        if file_size > current_app.config['PAGES_ATTACHMENT_MAX_SIZE']:
            return False
    else:
        size = 0
        for upload in attachments:
            upload.seek(current_app.config['PAGES_ATTACHMENT_MAX_SIZE'] -
                        size)
            if upload.read(1) == '':
                return False

            size += len(upload)
    return True


def send_support_email(context):
    """Signal for sending emails after contact form validated.

    :param context: Dictionary with email information.
    """
    msg_body = format_request_email_body(context)
    msg_title = format_request_email_title(context)

    msg = Message(
        msg_title,
        sender=current_app.config['PAGES_SENDER_EMAIL'],
        recipients=current_app.config['PAGES_SUPPORT_EMAIL'],
        reply_to=context.get('info').get('email'),
        body=msg_body
    )

    attachments = request.files.getlist("attachments")
    if attachments:
        for upload in attachments:
            msg.attach(upload.filename,
                       'application/octet-stream',
                       upload.read())

    current_app.extensions['mail'].send(msg)


def format_uap_info(info):
    """Format a ua-parser field.

    :param info: Dictionary of ua-parser field.
    :returns: Return user agent parsed string.
    :rtype: str
    """
    info_version = '.'.join(
        [v for v in (info.get('major'), info.get('minor'),
                     info.get('patch')) if v]
    )

    return '{info} {info_version}'.format(
        info=info.get('family'),
        info_version=info_version
    )


def user_agent_information():
    """Function to get user agent information.

    :returns: Dictionary with user agent information.
    :rtype: dict
    """
    uap = user_agent_parser.Parse(str(request.user_agent))

    # Operating System and it's version.
    os = format_uap_info(uap.get('os'))

    # Browser and it's version.
    browser = format_uap_info(uap.get('user_agent'))

    # Device, it's model and brand.
    device = ' '.join(
        [v for v in (
            uap.get('device').get('family'),
            uap.get('device').get('brand'),
            uap.get('device').get('model')
            ) if v]
    )
    return dict(os=os, browser=browser, device=device)
