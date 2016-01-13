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

"""Blueprint for Zenodo-Records."""

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify, request
from invenio_search import Query, current_search_client

blueprint = Blueprint(
    'zenodo_search_ui',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/search2',
)


@blueprint.route('/api', methods=['GET', 'POST'])
def api():
    """Search API for search UI demo.

    .. note::

        WARNING! This search API is just for demo proposes only.

    """
    page = request.values.get('page', 1, type=int)
    size = request.values.get('size', 1, type=int)
    query = Query(request.values.get('q', ''))[(page-1)*size:page*size]
    # dummy facets
    query.body["aggs"] = {
        "by_body": {
            "terms": {
                "field": "summary.summary"
            }
        },
        "by_title": {
            "terms": {
                "field": "title_statement.title"
            }
        }
    }
    response = current_search_client.search(
        index=request.values.get('index', 'records'),
        doc_type=request.values.get('type'),
        body=query.body,
    )
    return jsonify(**response)
