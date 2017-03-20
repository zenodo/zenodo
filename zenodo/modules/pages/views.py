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

"""Zenodo pages."""

from __future__ import absolute_import, print_function

import json

from flask import Blueprint, current_app, flash, redirect, render_template, \
    request
from flask_babelex import lazy_gettext as _
from flask_mail import Message
from flask_security import current_user

from .forms import contact_form_factory
from .utils import send_support_email

blueprint = Blueprint(
    'zenodo_pages',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route(
    '/support',
    methods=['GET', 'POST']
)
def support():
    """Render contact form."""
    form_class = contact_form_factory()
    form = form_class()

    if form.include_os_browser.data:
        form.os.data = request.user_agent.platform
        form.browser.data = request.user_agent.browser
        form.version.data = request.user_agent.version
    if current_user.is_authenticated:
        form.email.data = current_user.email

    """If form is validated send email to the admin."""
    if form.validate_on_submit():
        """Dictionary storing data to be sent."""
        context = dict(
            form=form,
            current_user=current_user,
        )

        send_support_email(context)

        flash(
            _('Request sent successfully,'
              'You should receive a confirmation email within 20 minutes - '
              'if this does not happen you should retry or send us an email '
              'directly to team@zenodo.org.',),
            category='success'
        )
        return redirect('/')

    content = current_app.config['PAGES_ISSUE_CATEGORY']
    return render_template(
        'zenodo_pages/contact_form.html',
        form=form,
        current_user=current_user,
        content=json.dumps(content),
    )
