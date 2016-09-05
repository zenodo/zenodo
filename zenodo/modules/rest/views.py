# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Root REST API endpoint for Zenodo."""

from __future__ import absolute_import, print_function

from flask import Blueprint, Response, current_app, json, request, url_for

blueprint = Blueprint(
    'zenodo_rest',
    __name__,
    url_prefix='',
)


def _format_args():
    """Get JSON dump indentation and separates."""
    # Ensure we can run outside a application/request context.
    try:
        pretty_format = \
            current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and \
            not request.is_xhr
    except RuntimeError:
        pretty_format = False

    if pretty_format:
        return dict(
            indent=2,
            separators=(', ', ': '),
        )
    else:
        return dict(
            indent=None,
            separators=(',', ':'),
        )


@blueprint.route('/')
def index():
    """REST API root endpoint."""
    return Response(
        json.dumps({
            'links': {
                'communities': url_for(
                    'invenio_communities_rest.communities_list',
                    _external=True),
                'deposits': url_for(
                    'invenio_deposit_rest.depid_list', _external=True),
                'funders': url_for(
                    'invenio_records_rest.frdoi_list', _external=True),
                'grants': url_for(
                    'invenio_records_rest.grant_list', _external=True),
                'files': url_for(
                    'invenio_files_rest.location_api', _external=True),
                'licenses': url_for(
                    'invenio_records_rest.od_lic_list', _external=True),
                'records': url_for(
                    'invenio_records_rest.recid_list', _external=True), }
            },
            **_format_args()
        ),
        mimetype='application/json',
    )
