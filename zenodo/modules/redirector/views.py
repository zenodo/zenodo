# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Zenodo redirector."""

from __future__ import absolute_import, print_function

from flask import Blueprint, redirect, request, url_for
from invenio_search_ui.views import search as search_ui_search

from .config import ZENODO_TYPE_SUBTYPE_LEGACY

blueprint = Blueprint(
    'zenodo_redirector',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.record_once
def configure_search_handler(blueprint_setup):
    """Update the search endpoint."""
    blueprint_setup.app.view_functions[
        'invenio_search_ui.search'] = search_handler


# https://zenodo.org/collection/user-<id>
# https://zenodo.org/communities/<id>/
@blueprint.route('/collection/user-<id>')
def community_redirect(id):
    """Redirect from the old community details to the new one."""
    values = request.args.to_dict()
    values['community_id'] = id
    return redirect(url_for('invenio_communities.detail', **values))


# https://zenodo.org/communities/about/<id>/
# https://zenodo.org/communities/<id>/about/
@blueprint.route('/communities/about/<id>/')
def communities_about_redirect(id):
    """."""
    values = request.args.to_dict()
    values['community_id'] = id
    return redirect(url_for('invenio_communities.about', **values))


# https://zenodo.org/collection/<type>
# https://zenodo.org/search?type=<general type>&subtype=<sub type>
@blueprint.route('/collection/<type>')
def collections_type_redirect(type):
    """."""
    values = request.args.to_dict()

    type, subtype = ZENODO_TYPE_SUBTYPE_LEGACY.get(type, ('', None))
    values['type'] = type
    if subtype:
        values['subtype'] = subtype

    return redirect(url_for('invenio_search_ui.search', **values))


def _pop_p(values):
    if 'p' in values:
        values['q'] = values.pop('p')
    values.pop('action_search', None)
    # May need to be removed later:
    values.pop('ln', None)


def search_handler():
    """Search handler."""
    if 'cc' in request.args:
        if request.args.get('cc', '').startswith('user-'):
            return community_search_redirect()
        elif request.args.get('cc', '').startswith('provisional-user-'):
            return communities_provisional_user_redirect()
        else:
            return collections_search_redirect()
    elif 'p' in request.args:
        values = request.args.to_dict()
        _pop_p(values)
        return redirect(url_for('invenio_search_ui.search', **values))
    else:
        return search_ui_search()


# https://zenodo.org/search?ln=en&cc=user-<id>&p=<query>&action_search=
# https://zenodo.org/communities/<id>/search?q=<query>
def community_search_redirect():
    """Redirect from the old community search to the new one."""
    values = request.args.to_dict()
    values['community_id'] = values.pop('cc')[5:]  # len('user-') == 5
    _pop_p(values)
    return redirect(url_for('invenio_communities.search', **values))


# https://zenodo.org/search?cc=provisional-user-<id>&p=<query>
# https://zenodo.org/communities/<id>/curate/?q=<query>
def communities_provisional_user_redirect():
    """Redirect from the old communities provisional search to the new one."""
    values = request.args.to_dict()
    # len('provisional-user-') == 17
    values['community_id'] = values.pop('cc')[17:]
    _pop_p(values)
    return redirect(url_for('invenio_communities.curate', **values))


# https://zenodo.org/search?ln=en&cc=<type>
# https://zenodo.org/search?type=<general type>&subtype=<sub type>
def collections_search_redirect():
    """."""
    values = request.args.to_dict()
    type, subtype = ZENODO_TYPE_SUBTYPE_LEGACY.get(
        values.pop('cc'), ('', None))
    values['type'] = type
    if subtype:
        values['subtype'] = subtype
    _pop_p(values)
    return redirect(url_for('invenio_search_ui.search', **values))
