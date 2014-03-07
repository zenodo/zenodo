# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
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

""" Zenodo Communities Blueprint """

from flask import Blueprint
from flask.ext.login import current_user

from invenio.ext.cache import cache
from invenio.modules.communities.models import Community
from invenio.base.signals import webcoll_after_webpage_cache_update
from invenio.modules.communities.signals import after_save_collection, \
    pre_curation, post_curation

from .receivers import invalidate_jinja2_cache, pre_curation_reject_listener, \
    post_curation_reject_listener


blueprint = Blueprint(
    'zenodo_communities',
    __name__,
    static_folder="static",
    template_folder="templates",
)


@blueprint.before_app_first_request
def register_receivers():
    """
    Setup signal receivers for communities module.
    """
    webcoll_after_webpage_cache_update.connect(invalidate_jinja2_cache)
    after_save_collection.connect(invalidate_jinja2_cache)
    pre_curation.connect(pre_curation_reject_listener)
    post_curation.connect(post_curation_reject_listener)
