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

"""Forms for pages module."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_babelex import lazy_gettext as _
from flask_security import current_user
from flask_wtf import FlaskForm, validators
from flask_wtf.file import FileField
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import BooleanField, SelectField, StringField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms_components import read_only

def strip_filter(text):
    """Filter for trimming whitespace."""
    return text.strip() if text else text

def contact_form_factory():
    """Contact form factory."""
    issue_choices = [(row[0], row[0]) for row in \
                     current_app.config['PAGES_ISSUE_CATEGORY']]
    min_length = current_app.config['PAGES_DESCRIPTION_MIN_LENGTH']
    max_length = current_app.config['PAGES_DESCRIPTION_MAX_LENGTH']


    class ContactForm(FlaskForm):
        """Form for contact form."""

        name = StringField(
            _('Name'),
            description=_(''),
            filters=[strip_filter],
            validators=[DataRequired()],
        )
        email = StringField(
            _('Email'),
            description=_(''),
            filters=[strip_filter],
            validators=[DataRequired()],
        )
        subject = StringField(
            _('Subject'),
            description=_(''),
            filters=[strip_filter],
            validators=[DataRequired()],
        )
        issue_category = SelectField(
            _('Select Category for Issue'),
            choices = issue_choices,
            validators = [DataRequired()],
        )
        description = TextAreaField(
            _('How can we help?'),
            description=_(''),
            filters=[strip_filter],
            validators = [Length(
                min=min_length,
                max=max_length)],
        )
        include_os_browser = BooleanField(
            _('Include browser and operating system information'),
            default="checked",
        )
        os = StringField(_('Operating System'),)
        browser = StringField(_('Browser'),)
        version = StringField(_('Version'))
        submit = SubmitField(_("Send Request"))
        attachments = FileField()
        recaptcha = RecaptchaField(validators=[
            Recaptcha(message=_("Please complete the reCAPTCHA."))
        ])

        def __init__(self, *args, **kwargs):
            """For read_only attribute in form fields."""
            super(ContactForm, self).__init__(*args, **kwargs)
            read_only(self.os)
            read_only(self.browser)
            read_only(self.version)

    return ContactForm
