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

"""Zenodo Pages."""

from __future__ import absolute_import, print_function

from collections import OrderedDict

from flask import Blueprint, current_app, flash, redirect, render_template, \
    request, url_for
from flask_babelex import lazy_gettext as _
from flask_security import current_user
from jinja2.filters import do_filesizeformat
from wtforms.validators import Length

from .forms import ContactForm
from .utils import check_attachment_size, send_support_email, \
    user_agent_information

blueprint = Blueprint(
    'zenodo_pages',
    __name__,
    template_folder='templates',
)


@blueprint.route('/support', methods=['GET', 'POST'])
def support():
    """Render contact form."""
    form = ContactForm()
    if current_user.is_authenticated:
        user_id = current_user.id
        form.email.data = current_user.email
        form.name.data = form.name.data or (current_user.profile.full_name
                                            if current_user.profile else None)
        form.recaptcha.validators = []
    else:
        user_id = None

    uap = user_agent_information()

    # Load form choices and validation from config
    categories = OrderedDict(
        (c['key'], c) for c in current_app.config['PAGES_ISSUE_CATEGORIES'])
    form.issue_category.choices = \
        [(c['key'], c['title']) for c in categories.values()]
    form.description.validators.append(Length(
        min=current_app.config['PAGES_DESCRIPTION_MIN_LENGTH'],
        max=current_app.config['PAGES_DESCRIPTION_MAX_LENGTH'],
    ))
    form.attachments.description = 'Optional. Max attachments size: ' + \
        do_filesizeformat(current_app.config['PAGES_ATTACHMENT_MAX_SIZE'])

    if form.validate_on_submit():
        attachments = request.files.getlist("attachments")
        if attachments and not check_attachment_size(attachments):
            form.attachments.errors.append('File size exceeded. '
                                           'Please add URLs to the files '
                                           'or make a smaller selection.')
        else:
            context = dict(user_id=user_id, info=form.data, uap=uap)
            recipients = categories[form.issue_category.data]['recipients']
            send_support_email(context, recipients)
            flash(
                _('Request sent successfully, '
                  'You should receive a confirmation email within 20 minutes '
                  '- if this does not happen you should retry or send us an '
                  'email directly to info@zenodo.org.'),
                category='success'
            )
            return redirect(url_for('zenodo_frontpage.index'))
    return render_template(
        'zenodo_pages/contact_form.html',
        uap=uap,
        form=form,
        categories=categories,
        max_file_size=current_app.config['PAGES_ATTACHMENT_MAX_SIZE'],
    )
