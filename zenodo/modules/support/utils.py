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

"""Utils for Zenodo support module."""

from __future__ import absolute_import, print_function, unicode_literals

import bleach
from flask import current_app, request
from flask_mail import Message
from ua_parser import user_agent_parser

from zenodo.modules.records.serializers.fields.html import ALLOWED_ATTRS, \
    ALLOWED_TAGS

from .proxies import current_support_categories


def render_template_to_string(template, context):
    """Render a Jinja template with the given context."""
    template = current_app.jinja_env.get_or_select_template(template)
    return template.render(context)


def check_attachment_size(attachment_files):
    """Function to check size of attachment within limits."""
    if len(attachment_files) == 0:
        return False
    if request.content_length:
        file_size = int(request.content_length)
        if file_size > current_app.config['SUPPORT_ATTACHMENT_MAX_SIZE']:
            return False
    else:
        size = 0
        for f in attachment_files:
            f.seek(current_app.config['SUPPORT_ATTACHMENT_MAX_SIZE'] - size)
            if f.read(1) == '':
                return False
            size += len(f)
    return True


def format_user_email(email, name):
    """Format the user's email as 'Full Name <email>' or 'email'."""
    if name:
        email = '{name} <{email}>'.format(name=name, email=email)
    # Remove commas (',') since they mess with the "TO" email field
    return email.replace(',', '')


def format_user_email_ctx(context):
    """Format the user's email from form context."""
    return format_user_email(
        context.get('info', {}).get('email'),
        context.get('info', {}).get('name', None)
    )


def get_support_email_recipients(context):
    """Return recipients for the support email."""
    issue_category = context.get('info', {}).get('issue_category')
    category_config = current_support_categories.get(issue_category, {})
    return category_config.get(
        'recipients', current_app.config['SUPPORT_SUPPORT_EMAIL'])


def send_support_email(context):
    """Signal for sending emails after contact form validated."""
    sanitized_description = bleach.clean(
            context['info']['description'],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            strip=True,
        ).strip()
    context['info']['description'] = sanitized_description

    msg_body = render_template_to_string(
        current_app.config['SUPPORT_EMAIL_BODY_TEMPLATE'], context)
    msg_title = render_template_to_string(
        current_app.config['SUPPORT_EMAIL_TITLE_TEMPLATE'], context)
    sender = format_user_email_ctx(context)
    recipients = get_support_email_recipients(context)

    msg = Message(
        msg_title,
        sender=sender,
        recipients=recipients,
        reply_to=context.get('info', {}).get('email'),
        body=msg_body
    )

    attachments = request.files.getlist("attachments")
    if attachments:
        for upload in attachments:
            msg.attach(upload.filename,
                       'application/octet-stream',
                       upload.read())

    current_app.extensions['mail'].send(msg)


def send_confirmation_email(context):
    """Sending support confirmation email."""
    recipient = format_user_email_ctx(context)
    sender = format_user_email(
        current_app.config['SUPPORT_SENDER_EMAIL'],
        current_app.config['SUPPORT_SENDER_NAME']
    )
    title = current_app.config['SUPPORT_EMAIL_CONFIRM_TITLE']
    body = current_app.config['SUPPORT_EMAIL_CONFIRM_BODY']
    msg = Message(
        title,
        body=body,
        sender=sender,
        recipients=[recipient, ],
    )
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
    os = format_uap_info(uap.get('os'))
    browser = format_uap_info(uap.get('user_agent'))
    device = ' '.join(
        [v for v in (
            uap.get('device').get('family'),
            uap.get('device').get('brand'),
            uap.get('device').get('model')
            ) if v]
    )
    return dict(os=os, browser=browser, device=device)
