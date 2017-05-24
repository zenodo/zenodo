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

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, jsonify, request
from flask_login import login_required
from invenio_communities.views.ui import pass_community, permission_required
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning

from zenodo.modules.communities.api import ZenodoCommunity
from zenodo.modules.records.resolvers import record_resolver

blueprint = Blueprint(
    'zenodo_communities',
    __name__,
    url_prefix='/communities',
    # template_folder='../templates',
    # static_folder='../static',
)


@blueprint.route('/<string:community_id>/curaterecord/', methods=['POST'])
@login_required
@pass_community
@permission_required('community-curate')
def curate(community):
    """Index page with uploader and list of existing depositions.

    :param community_id: ID of the community to curate.
    """
    action = request.json.get('action')
    recid = request.json.get('recid')
    if not recid:
        abort(400)
    if action not in ['accept', 'reject', 'remove']:
        abort(400)

    # Resolve recid to a Record
    pid, record = record_resolver.resolve(recid)

    # Perform actions
    pv = PIDVersioning(child=pid)
    if pv.exists:
        api = ZenodoCommunity(community)
    else:
        api = community
    if action == "accept":
        api.accept_record(record, pid=pid)
    elif action == "reject":
        api.reject_record(record, pid=pid)
    elif action == "remove":
        api.remove_record(record, pid=pid)

    db.session.commit()
    RecordIndexer().index_by_id(record.id)
    return jsonify({'status': 'success'})
