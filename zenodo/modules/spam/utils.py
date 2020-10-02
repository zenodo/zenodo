# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2020 CERN.
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

"""Forms for spam deletion module."""

from __future__ import absolute_import, print_function

from flask import current_app, render_template
from flask_babelex import gettext as _
from flask_mail import Message
from invenio_mail.tasks import send_email


def send_spam_user_email(recipient):
    """Send email notification to blocked user after spam detection."""
    msg = Message(
        _("Your Zenodo Upload has been automatically marked as Spam."),
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=[recipient],
    )
    msg.body = render_template("zenodo_spam/email/spam_user_email.tpl")
    send_email.delay(msg.__dict__)


def send_spam_admin_email(deposit, user):
    """Send email notification to admins for a spam detection."""
    msg = Message(
        _("Zenodo Deposit Marked as Spam."),
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=[current_app.config.get('ZENODO_ADMIN_EMAIL')],
    )
    msg.body = render_template(
        "zenodo_spam/email/spam_admin_email.tpl",
        user=user,
        deposit=deposit)
    send_email.delay(msg.__dict__)
