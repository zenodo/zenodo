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

from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import BooleanField, SelectField, StringField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired


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
        _('Category for Issue'),
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
        _('Include browser and operating system information'),
        default="checked",
    )

    submit = SubmitField(_('Send Request'))

    attachments = FileField(
        _('Attachments'),
        render_kw={'multiple': True},
    )

    recaptcha = RecaptchaField(validators=[
        Recaptcha(message=_("Please complete the reCAPTCHA."))
    ])
