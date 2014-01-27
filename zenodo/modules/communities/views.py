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


@blueprint.app_template_filter('community_id')
def community_id(coll):
    """
    Determine if current user is owner of a given record

    @param coll: Collection object
    """
    if coll:
        identifier = coll.name
        if identifier.startswith("provisional-user-"):
            return identifier[len("provisional-user-"):]
        elif identifier.startswith("user-"):
            return identifier[len("user-"):]
    return ""


@blueprint.app_template_filter('curation_action')
def curation_action(recid, ucoll_id=None):
    """
    Determine if curation action is underway
    """
    return cache.get("usercoll_curate:%s_%s" % (ucoll_id, recid))


@blueprint.app_template_filter('community_state')
def community_state(bfo, ucoll_id=None):
    """
    Determine if current user is owner of a given record

    @param coll: Collection object
    """
    coll_id_reject = "provisional-user-%s" % ucoll_id
    coll_id_accept = "user-%s" % ucoll_id

    for cid in bfo.fields('980__a'):
        if cid == coll_id_accept:
            return "accepted"
        elif cid == coll_id_reject:
            return "provisional"
    return "rejected"


@blueprint.app_template_filter('communities')
def communities(bfo, is_owner=False, provisional=False, public=True,
                filter_zenodo=False):
    """
    Maps collection identifiers to community collection objects

    @param bfo: BibFormat Object
    @param is_owner: Set to true to only return user collections which the
                     current user owns.
    @oaram provisional: Return provisional collections (default to false)
    @oaram public: Return public collections (default to true)
    """
    colls = []
    if is_owner and current_user.is_guest:
        return colls

    for cid in bfo.fields('980__a'):
        # Remove zenodo collections from ab
        if filter_zenodo and (cid == 'user-zenodo' or
           cid == 'provisional-user-zenodo'):
            continue
        if provisional and cid.startswith('provisional-'):
            colls.append(cid[len("provisional-user-"):])
        elif public and cid.startswith('user-'):
            colls.append(cid[len("user-"):])

    query = [Community.id.in_(colls)]
    if is_owner:
        query.append(Community.id_user == current_user.get_id())

    return Community.query.filter(*query).all()
