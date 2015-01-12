# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""DOI Badge Blueprint."""

from __future__ import absolute_import

import os
import urllib

from flask import Blueprint, make_response, abort, current_app, redirect, \
    url_for

from invenio.modules.pidstore.models import PersistentIdentifier
from invenio.ext.sslify import ssl_required

from ..helpers import get_account
from ..badge import create_badge

blueprint = Blueprint(
    'zenodo_github_badge',
    __name__,
    url_prefix="/badge",
    static_folder="../static",
    template_folder="../templates",
)


def badge(doi):
    """Helper method to generate DOI badge."""
    doi_encoded = urllib.quote(doi, '')

    # Check if badge already exists
    badge_path = os.path.join(
        current_app.config['COLLECT_STATIC_ROOT'],
        "badges",
        "%s.svg" % doi_encoded
    )

    if not os.path.exists(os.path.dirname(badge_path)):
        os.makedirs(os.path.dirname(badge_path))

    if not os.path.isfile(badge_path):
        create_badge(doi, badge_path)

    resp = make_response(open(badge_path, 'r').read())
    resp.content_type = "image/svg+xml"
    return resp


#
# Views
#
@blueprint.route("/<int:user_id>/<path:repository>.svg", methods=["GET"])
@ssl_required
def index(user_id, repository):
    """Generate a badge for a specific GitHub repository."""
    account = get_account(user_id=user_id)

    if repository not in account.extra_data["repos"]:
        return abort(404)

    # Get the latest deposition
    dep = account.extra_data["repos"][repository]['depositions'][-1]

    # Extract DOI
    if "doi" not in dep:
        return abort(404)

    doi = dep["doi"]

    return badge(doi)


@blueprint.route("/doi/<path:doi>.svg", methods=["GET"])
@ssl_required
def doi_badge(doi):
    """Generate a badge for a specific DOI."""
    pid = PersistentIdentifier.get("doi", doi)

    if pid is None:
        return abort(404)
    return badge(doi)


@blueprint.route("/<int:user_id>/<path:repository>.png", methods=["GET"])
@ssl_required
def index_old(user_id, repository):
    """Legacy support for old badge icons."""
    return redirect(url_for('.index', user_id=user_id, repository=repository))


@blueprint.route("/doi/<path:doi>.png", methods=["GET"])
@ssl_required
def doi_badge_old(doi):
    """Legacy support for old badge icons."""
    return redirect(url_for('.doi_badge', doi=doi))
