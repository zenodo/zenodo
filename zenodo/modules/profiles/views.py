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

from flask import Blueprint, flash, redirect, render_template
from flask_babelex import lazy_gettext as _

from .forms import ContactOwnerForm

blueprint = Blueprint(
    'zenodo_profiles',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route(
    '/profile/<int:owner_id>/search',
    methods=['GET']
)
def profile_search(owner_id):
    """Render profile search page."""
    user = {
        'id': '1161',
        'name': 'Aman Jain',
        'affiliation': 'BVCOE, Paschim Vihar',
        'description': 'I am enthusiast coder and web developer with an urge '
        'to create something new and useful. Looking to contribute in good '
        'opensource projects. GSoCer with Zenodo.',
        'image':
        'https://avatars3.githubusercontent.com/u/13117482?v=3&amp;s=460',
        'location': 'Delhi, India',
        'website': 'http://jainaman224.me',
        'orcid_account': 'http://orcid.org/0000-0001-9619-2956',
        'github_account': 'http://github.com/jainaman224',
        'organization': [
            {
                'name': 'Zenodo',
                'link': 'https://zenodo.org/communities/zenodo/'
            },
            {
                'name': 'Biodiversity Literature Repository',
                'link': 'https://zenodo.org/communities/biosyslit'
            },
            {
                'name': 'European Commission Funded Research (OpenAIRE)',
                'link': 'https://zenodo.org/communities/ecfunded/'
            },
            {
                'name': 'Human Brain Project',
                'link': 'https://zenodo.org/communities/hbp/'
            }
        ]
    }
    return render_template(
        'zenodo_profiles/search.html',
        user=user
    )


@blueprint.route(
    '/profile/<int:owner_id>',
    methods=['GET']
)
def profile(owner_id):
    """Render profile page."""
    user = {
        'id': '1161',
        'name': 'Aman Jain',
        'affiliation': 'BVCOE, Paschim Vihar',
        'description': 'I am enthusiast coder and web developer with an urge '
        'to create something new and useful. Looking to contribute in good '
        'opensource projects. GSoCer with Zenodo.',
        'image':
        'https://avatars3.githubusercontent.com/u/13117482?v=3&amp;s=460',
        'location': 'Delhi, India',
        'website': 'http://jainaman224.me',
        'orcid_account': 'http://orcid.org/0000-0001-9619-2956',
        'github_account': 'http://github.com/jainaman224',
        'organization': [
            {
                'name': 'Zenodo',
                'link': 'https://zenodo.org/communities/zenodo/'
            },
            {
                'name': 'Biodiversity Literature Repository',
                'link': 'https://zenodo.org/communities/biosyslit'
            },
            {
                'name': 'European Commission Funded Research (OpenAIRE)',
                'link': 'https://zenodo.org/communities/ecfunded/'
            },
            {
                'name': 'Human Brain Project',
                'link': 'https://zenodo.org/communities/hbp/'
            }
        ]
    }
    return render_template(
        'zenodo_profiles/profile.html',
        user=user
    )


@blueprint.route(
    '/profile/<int:owner_id>/contact',
    methods=['GET', 'POST']
)
def profile_contact(owner_id):
    """Render contact owner form."""
    form = ContactOwnerForm()
    if form.validate_on_submit():
        flash(
            _('Request sent successfully.'),
            category='success'
        )
        return redirect('/')

    user = {
        'id': '1161',
        'name': 'Aman Jain',
        'affiliation': 'BVCOE, Paschim Vihar',
        'description': 'I am enthusiast coder and web developer with an urge '
        'to create something new and useful. Looking to contribute in good '
        'opensource projects. GSoCer with Zenodo.',
        'image':
        'https://avatars3.githubusercontent.com/u/13117482?v=3&amp;s=460',
        'location': 'Delhi, India',
        'website': 'http://jainaman224.me',
        'orcid_account': 'http://orcid.org/0000-0001-9619-2956',
        'github_account': 'http://github.com/jainaman224',
        'organization': [
            {
                'name': 'Zenodo',
                'link': 'https://zenodo.org/communities/zenodo/'
            },
            {
                'name': 'Biodiversity Literature Repository',
                'link': 'https://zenodo.org/communities/biosyslit'
            },
            {
                'name': 'European Commission Funded Research (OpenAIRE)',
                'link': 'https://zenodo.org/communities/ecfunded/'
            },
            {
                'name': 'Human Brain Project',
                'link': 'https://zenodo.org/communities/hbp/'
            }
        ]
    }
    return render_template(
        'zenodo_profiles/contact.html',
        user=user,
        form=form
    )
