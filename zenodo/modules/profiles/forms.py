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

"""Forms for owner module."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_babelex import lazy_gettext as _
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from invenio_userprofiles.forms import EmailProfileForm, ProfileForm
from wtforms import BooleanField, StringField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired


def strip_filter(text):
    """Filter for trimming whitespace."""
    return text.strip() if text else text


class ContactOwnerForm(FlaskForm):
    """Form for contact owner form."""

    field_sets = ['name', 'subject', 'body', 'recaptcha']

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

    subject = StringField(
        _('Subject'),
        description=_('Required.'),
        filters=[strip_filter],
        validators=[DataRequired()],
    )

    body = TextAreaField(
        _('Your message to the author'),
        description=_('Required.'),
        filters=[strip_filter],
        validators=[DataRequired()],
    )

    submit = SubmitField(_('Send Request'))

    recaptcha = RecaptchaField(validators=[
        Recaptcha(message=_("Please complete the reCAPTCHA."))
    ])


class ResearcherProfileForm(FlaskForm):
    """Form for Profiles class."""

    bio = TextAreaField(
        _('Short Bio'),
        description=_('Optional'),
        filters=[strip_filter]
    )

    affiliation = StringField(
        _('Affiliation'),
        description=_('Optional'),
        filters=[strip_filter]
    )

    location = StringField(
        _('Location'),
        description=_('Optional'),
        filters=[strip_filter]
    )

    website = StringField(
        _('Website'),
        description=_('Optional'),
        filters=[strip_filter]
    )

    show_profile = BooleanField(
        _('Show Profile')
    )

    allow_contact_owner = BooleanField(
        _('Allow other users to contact'),
    )


class EmailResearcherForm(EmailProfileForm, ResearcherProfileForm):
    """."""

    field_sets = ['csrf_token', 'username', 'full_name', 'email',
                  'email_repeat', 'show_profile', 'bio', 'affiliation',
                  'location', 'website', 'allow_contact_owner']

    #
    # Methods
    #
    def get_field_by_name(self, name):
        """Return field by name."""
        try:
            return self._fields[name]
        except KeyError:
            return None


class ResearcherForm(ProfileForm, ResearcherProfileForm):
    """."""

    field_sets = [
        'csrf_token', 'username', 'full_name', 'show_profile', 'bio',
        'affiliation', 'location', 'website',  'allow_contact_owner']

    #
    # Methods
    #
    def get_field_by_name(self, name):
        """Return field by name."""
        try:
            return self._fields[name]
        except KeyError:
            return None


def profile_form_factory():
    """Create a profile page form."""
    if current_app.config['USERPROFILES_EMAIL_ENABLED']:
        return EmailResearcherForm(
            formdata=None,
            username=current_user.profile.username,
            full_name=current_user.profile.full_name,
            email=current_user.email,
            email_repeat=current_user.email,
            bio=current_user.researcher_profile.bio,
            affiliation=current_user.researcher_profile.affiliation,
            location=current_user.researcher_profile.location,
            website=current_user.researcher_profile.website,
            show_profile=current_user.researcher_profile.show_profile,
            allow_contact_owner=(
                current_user.researcher_profile.allow_contact_owner
            ),
            prefix='profile'
        )
    else:
        return ResearcherForm(
            formdata=None,
            username=current_user.profile.username,
            full_name=current_user.profile.full_name,
            bio=current_user.researcher_profile.bio,
            affiliation=current_user.researcher_profile.affiliation,
            location=current_user.researcher_profile.location,
            website=current_user.researcher_profile.website,
            show_profile=current_user.researcher_profile.show_profile,
            allow_contact_owner=(
                current_user.researcher_profile.allow_contact_owner
            ),
            prefix='profile'
        )
