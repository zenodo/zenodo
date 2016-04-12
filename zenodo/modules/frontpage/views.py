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

from flask import Blueprint, render_template
from flask_menu import register_menu
from invenio_search import Query, current_search_client

blueprint = Blueprint(
    'zenodo_frontpage',
    __name__,
    url_prefix='',
    template_folder='templates',
)


@blueprint.route('/')
def index():
    """Frontpage blueprint."""
    query = Query("communities:zenodo AND access_right:open")
    query.body["size"] = 10
    query.body["sort"] = [{"_created": "desc"}]

    response = current_search_client.search(
        index='records',
        body=query.body,
    )

    return render_template(
        'zenodo_frontpage/index.html',
        records=(h['_source'] for h in response['hits']['hits'])
    )


@blueprint.route('/ping', methods=['HEAD', 'GET'])
def ping():
    """Frontpage blueprint."""
    return 'OK'


@blueprint.route('/deposit/')
@register_menu(blueprint, 'main.upload', 'Upload', order=2)
def index2():
    """Frontpage blueprint."""
    return render_template('invenio_deposit/index.html')


@blueprint.route('/communities/')
@register_menu(blueprint, 'main.communities', 'Communities', order=3)
def index3():
    """Frontpage blueprint."""
    return render_template('zenodo_frontpage/coming_soon.html')
