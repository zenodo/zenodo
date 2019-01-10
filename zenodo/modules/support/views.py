# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo support views."""

from __future__ import absolute_import, print_function

import smtplib

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babelex import lazy_gettext as _
from flask_security import current_user

from .forms import contact_form_factory
from .proxies import current_support_categories
from .utils import check_attachment_size, send_confirmation_email, \
    send_support_email, user_agent_information

blueprint = Blueprint(
    'zenodo_support',
    __name__,
    template_folder='templates',
)


@blueprint.route('/support', methods=['GET', 'POST'])
def support():
    """Render contact form."""
    uap = user_agent_information()
    form = contact_form_factory()
    if form.validate_on_submit():
        attachments = request.files.getlist("attachments")
        if attachments and not check_attachment_size(attachments):
            form.attachments.errors.append('File size exceeded. '
                                           'Please add URLs to the files '
                                           'or make a smaller selection.')
        else:
            context = {
                'user_id': current_user.get_id(),
                'info': form.data,
                'uap': uap
            }
            
            try:
                send_support_email(context)
                send_confirmation_email(context)
            except smtplib.SMTPSenderRefused:
                flash(
                    _('There was an issue sending an email to the provided '
                      'address, please make sure it is correct. '
                      'If this issue persists you can send '
                      'us an email directly to info@zenodo.org.'),
                    category='danger'
                )
            except Exception:
                flash(
                    _("There was an issue sending the support request."
                      'If this issue persists send '
                      'us an email directly to info@zenodo.org.'),
                    category='danger'
                )
                raise
            else:
                flash(
                    _('Request sent successfully. '
                      'You should receive a confirmation email within several '
                      'minutes - if this does not happen you should retry or '
                      'send us an email directly to info@zenodo.org.'),
                    category='success'
                )
                return redirect(url_for('zenodo_frontpage.index'))
    return render_template(
        'zenodo_support/contact_form.html',
        uap=uap,
        form=form,
        categories=current_support_categories
    )
