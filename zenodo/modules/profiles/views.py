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

"""Zenodo profiles."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, flash, redirect, render_template, request
from flask_babelex import lazy_gettext as _
from flask_login import current_user, login_required
from flask_security.confirmable import send_confirmation_instructions
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import UserIdentity
from invenio_userprofiles.api import current_userprofile

from zenodo.modules.profiles.api import ResearcherRecordsSearch
from zenodo.modules.profiles.forms import ContactOwnerForm
from zenodo.modules.profiles.models import Profile
from zenodo.modules.profiles.utils import gravatar_url, send_support_email, \
    show_profile, user_orcid_id

blueprint = Blueprint(
    'zenodo_profiles',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route(
    '/profile/<int:owner_id>',
    methods=['GET']
)
@blueprint.route(
    '/profile/<orcid:orcid_id>',
    methods=['GET']
)
def profile(owner_id=None, orcid_id=None):
    """Render profile page."""
    if orcid_id is not None:
        orcid = UserIdentity.query.get((orcid_id, 'orcid'))
        if orcid:
            user = User.query.get(orcid.id_user)
        if not (orcid and show_profile(user)):
            return render_template(
                'zenodo_profiles/orcid_profile.html',
                profile_pic_url='http://www.gravatar.com/avatar?size=220',
                orcid_id=orcid_id,
                records=ResearcherRecordsSearch(orcid_id=orcid_id).sort(
                    '-_created').execute()[:10]
            )

    if owner_id is not None:
        user = User.query.get(owner_id)
    if not show_profile(user):
        abort(404)

    orcid_id = user_orcid_id(user, orcid_id)

    return render_template(
        'zenodo_profiles/profile.html',
        user=user,
        profile_pic_url=gravatar_url(user.email, 220),
        records=ResearcherRecordsSearch(
            user_id=user.id, orcid_id=orcid_id).sort(
                '-_created').execute()[:10]
    )


@blueprint.route(
    '/profile/<int:owner_id>/search',
    methods=['GET']
)
@blueprint.route(
    '/profile/<orcid:orcid_id>/search',
    methods=['GET']
)
def profile_search(owner_id=None, orcid_id=None):
    """Render profile search page."""
    if orcid_id is not None:
        orcid = UserIdentity.query.get((orcid_id, 'orcid'))
        if orcid:
            user = User.query.get(orcid.id_user)
        if not (orcid and show_profile(user)):
            return render_template(
                'zenodo_profiles/orcid_search.html',
                orcid_id=orcid_id
            )
    if owner_id is not None:
        user = User.query.get(owner_id)
    if not show_profile(user):
        abort(404)

    orcid_id = user_orcid_id(user, orcid_id)

    return render_template(
        'zenodo_profiles/search.html',
        user=user,
        orcid_id=orcid_id
    )


@blueprint.route(
    '/profile/<int:owner_id>/contact',
    methods=['GET', 'POST']
)
@login_required
def profile_contact(owner_id):
    """Render contact owner form."""
    form = ContactOwnerForm()
    user = User.query.get(owner_id)
    if form.validate_on_submit():
        context = dict(
            current_user=current_user,
            user=user,
            content=form.data
        )
        send_support_email(context)
        flash(
            _('Request sent successfully.'),
            category='success'
        )
        return redirect('/')

    if not (show_profile(user)
            and user.researcher_profile.allow_contact_owner):
        abort(404)

    return render_template(
        'zenodo_profiles/contact.html',
        user=user,
        form=form
    )


def handle_profile_form(form):
    """Handle profile update form."""
    form.process(formdata=request.form)

    if form.validate_on_submit():
        email_changed = False
        with db.session.begin_nested():
            # Update profile.
            current_userprofile.username = form.username.data
            current_userprofile.full_name = form.full_name.data
            db.session.add(current_userprofile)

            # Update researcher profile.
            researcher_profile = Profile.get_by_userid(
                current_user.researcher_profile.user_id
            )

            researcher_profile.show_profile = form.show_profile.data
            if form.show_profile.data:
                researcher_profile.bio = form.bio.data
                researcher_profile.affiliation = form.affiliation.data
                researcher_profile.location = form.location.data
                researcher_profile.website = form.website.data
                researcher_profile.allow_contact_owner = \
                    form.allow_contact_owner.data
            db.session.add(researcher_profile)

            # Update email
            if form.email.data != current_user.email:
                current_user.email = form.email.data
                current_user.confirmed_at = None
                db.session.add(current_user)
                email_changed = True
        db.session.commit()

        if email_changed:
            send_confirmation_instructions(current_user)
            # NOTE: Flash message after successful update of profile.
            flash(_('Profile was updated. We have sent a verification '
                    'email to %(email)s. Please check it.',
                    email=current_user.email),
                  category='success')
        else:
            # NOTE: Flash message after successful update of profile.
            flash(_('Profile was updated.'), category='success')
