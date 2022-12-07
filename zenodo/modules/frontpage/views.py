# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo frontpage blueprint."""

from __future__ import absolute_import, print_function

import os

from flask import Blueprint, current_app, flash, render_template, request, \
    send_from_directory, session
from flask_babelex import lazy_gettext as _
from flask_menu import current_menu
from invenio_communities.models import FeaturedCommunity

from ..records.resolvers import record_resolver
from .api import FrontpageRecordsSearch
from .decorators import cached_unless_authenticated_or_flashes

blueprint = Blueprint(
    'zenodo_frontpage',
    __name__,
    url_prefix='',
    template_folder='templates',
)


@blueprint.before_app_first_request
def init_menu():
    """Initialize menu before first request."""
    item = current_menu.submenu('main.deposit')
    item.register(
        'invenio_deposit_ui.index',
        _('Upload'),
        order=2,
    )
    item = current_menu.submenu('main.communities')
    item.register(
        'invenio_communities.index',
        _('Communities'),
        order=3,
    )


@blueprint.route('/')
@cached_unless_authenticated_or_flashes(timeout=600, key_prefix='frontpage')
def index():
    """Frontpage blueprint."""
    msg = current_app.config.get('FRONTPAGE_MESSAGE')
    if msg:
        flash(msg, category=current_app.config.get(
            'FRONTPAGE_MESSAGE_CATEGORY', 'info'))

    featured_comms_count = current_app.config.get(
        'ZENODO_FRONTPAGE_FEATURED_COMMUNITIES_COUNT', 3)
    featured_communities = [
        fc.community for fc in FeaturedCommunity.query.order_by(
            FeaturedCommunity.start_date.desc()).limit(featured_comms_count)
    ]
    featured_recids = current_app.config.get(
        'ZENODO_FRONTPAGE_FEATURED_RECORDS', [])
    featured_records = [record_resolver.resolve(r) for r in featured_recids]

    return render_template(
        'zenodo_frontpage/index.html',
        records=FrontpageRecordsSearch()[:10].sort('-_created').execute(),
        featured_communities=featured_communities,
        featured_records=featured_records,
    )


@blueprint.route('/favicon.ico')
def favicon():
    """Return the favicon."""
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@blueprint.route('/ping', methods=['HEAD', 'GET'])
def ping():
    """Load balancer ping view."""
    return 'OK'
