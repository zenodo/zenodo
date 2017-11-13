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

"""Forms for Zenodo Pages."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_babelex import lazy_gettext as _
from flask_security import current_user
from flask_wtf import FlaskForm, Recaptcha, RecaptchaField
from flask_wtf.file import FileField
from jinja2.filters import do_filesizeformat
from wtforms import BooleanField, SelectField, StringField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, Length

from .proxies import current_support_categories


def strip_filter(text):
    """Filter for trimming whitespace."""
    return text.strip() if text else text


class ContactForm(FlaskForm):
    """Form for contact form."""

    field_sets = ['name', 'email', 'subject', 'issue_category', 'description',
                  'attachments', 'include_os_browser', 'recaptcha']

    #
    # Methods
    #
    def get_field_by_name(self, name):
        """Return field by name."""
        try:
            return self._fields[name]
        except KeyError:
            return None

    #
    # Fields
    #
    name = StringField(
        _('Name'),
        description=_('Required.'),
        filters=[strip_filter],
        validators=[DataRequired()],
    )

    email = StringField(
        _('Email'),
        description=_('Required.'),
        filters=[strip_filter],
        validators=[DataRequired()],
    )

    subject = StringField(
        _('Subject'),
        description=_('Required.'),
        filters=[strip_filter],
        validators=[DataRequired()],
    )

    issue_category = SelectField(
        _('Category'),
        description=_('Required.'),
        coerce=str,
        validators=[DataRequired()],
    )

    description = TextAreaField(
        _('How can we help?'),
        description=_('Required.'),
        filters=[strip_filter],
    )

    include_os_browser = BooleanField(
        _('Browser & OS'),
        default="checked",
    )

    submit = SubmitField(_('Send Request'))

    attachments = FileField(
        _('Attachments'),
        render_kw={'multiple': True},
    )


class RecaptchaContactForm(ContactForm):
    """Recaptcha-enabled form."""
    recaptcha = RecaptchaField(validators=[
        Recaptcha(message=_("Please complete the reCAPTCHA."))
    ])


def contact_form_factory():
    """Return configured contact form."""
    if current_app.config.get('RECAPTCHA_PUBLIC_KEY') and \
            current_app.config.get('RECAPTCHA_PRIVATE_KEY') and \
            not current_user.is_authenticated:
        form = RecaptchaContactForm()
    else:
        form = ContactForm()

    if current_user.is_authenticated:
        form.email.data = current_user.email
        form.name.data = form.name.data or (current_user.profile.full_name
                                            if current_user.profile else None)

    # Load form choices and validation from config
    form.issue_category.choices = \
        [(c['key'], c['title']) for c in current_support_categories.values()]
    form.description.validators.append(Length(
        min=current_app.config['SUPPORT_DESCRIPTION_MIN_LENGTH'],
        max=current_app.config['SUPPORT_DESCRIPTION_MAX_LENGTH'],
    ))
    form.attachments.description = 'Optional. Max attachments size: ' + \
        do_filesizeformat(current_app.config['SUPPORT_ATTACHMENT_MAX_SIZE'])
    return form
