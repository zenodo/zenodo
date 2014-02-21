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


"""
Badge Blueprint
"""

from __future__ import absolute_import

import os
import json
import urllib

import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from flask import Blueprint, render_template, make_response
from flask.ext.login import login_required

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db

from zenodo.ext.oauth import oauth
from ..models import OAuthTokens


remote = oauth.remote_apps['github']
blueprint = Blueprint(
    'zenodo_github_badge',
    __name__,
    url_prefix="/badge",
    static_folder="../static",
    template_folder="../templates",
)

@blueprint.route("/<string:user_id>/<path:repository>", methods=["GET"])
def index(user_id, repository):
    user = OAuthTokens.query \
        .filter_by(
            user_id=user_id,
            client_id=remote.consumer_key
        ).first()
    
    if repository not in user.extra_data["repos"]:
        return json.dumps({})
    
    if "doi" not in user.extra_data["repos"][repository]:
        return json.dumps({})
    
    doi = user.extra_data["repos"][repository]["doi"]
    doi_encoded = urllib.quote(doi, '')
    
    badge_path = os.path.join(
        blueprint.static_folder, "badges", "%s.png" % doi_encoded
    )
    if os.path.isfile(badge_path):
        resp = make_response(open(badge_path, 'r').read())
        resp.content_type = "image/png"
        return resp
    
    font = ImageFont.truetype(
        os.path.join(blueprint.static_folder, "badges", "Trebuchet MS.ttf"),
        11
    )
    badge_template = os.path.join(blueprint.static_folder, "badges", "template.png")
    arr = np.asarray(
        Image.open(badge_template)
    )
    
    # Get left vertical strip for the DOI label
    label_strip = arr[:, 2]
    value_strip = arr[:, 3]
    
    # Splice into array
    label_width = 28
    value_width = 6 + font.getsize(doi)[0]
    
    # TODO: Use numpy repeat
    for i in xrange(label_width):
        arr = np.insert(arr, 3, label_strip, 1)
    for i in xrange(value_width):
        arr = np.insert(arr, label_width + 4, value_strip, 1)
    
    im = Image.fromarray(arr)
    draw = ImageDraw.Draw(im)
    draw.text(
        (6, 4),
        "DOI",
        (255, 255, 255),
        font=font
    )
    draw.text(
        (label_width + 8, 4),
        doi,
        (255, 255, 255),
        font=font
    )
    im.save(badge_path)
    
    resp = make_response(open(badge_path, 'r').read())
    resp.content_type = "image/png"
    return resp
