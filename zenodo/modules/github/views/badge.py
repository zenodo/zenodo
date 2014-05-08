# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


""" DOI Badge Blueprint. """

from __future__ import absolute_import

import os
import urllib

from flask import Blueprint, make_response, abort, current_app

from invenio.modules.pidstore.models import PersistentIdentifier

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
    """ Helper method to generate DOI badge. """
    doi_encoded = urllib.quote(doi, '')

    # Check if badge already exists
    badge_path = os.path.join(
        current_app.config['COLLECT_STATIC_ROOT'],
        "badges",
        "%s.png" % doi_encoded
    )

    font_path = os.path.join(
        blueprint.static_folder, "badges", "Trebuchet MS.ttf"
    )
    template_path = os.path.join(
        blueprint.static_folder, "badges", "template.png"
    )

    if not os.path.exists(os.path.dirname(badge_path)):
        os.makedirs(os.path.dirname(badge_path))

    if not os.path.isfile(badge_path):
        create_badge(doi, badge_path, font_path, template_path)

    resp = make_response(open(badge_path, 'r').read())
    resp.content_type = "image/png"
    return resp


#
# Views
#
@blueprint.route("/<int:user_id>/<path:repository>.png", methods=["GET"])
def index(user_id, repository):
    """ Generate a badge for a specific GitHub repository. """
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


@blueprint.route("/doi/<path:doi>.png", methods=["GET"])
def doi_badge(doi):
    """ Generate a badge for a specific DOI. """
    pid = PersistentIdentifier.get("doi", doi)

    if pid is None:
        return abort(404)
    return badge(doi)
