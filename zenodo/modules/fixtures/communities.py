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

"""Zenodo communities fixture loading."""

from __future__ import absolute_import, print_function


from invenio_db import db
from invenio_accounts.models import User
from invenio_communities.models import Community

from .utils import read_json


def loadcommunities(owner_email):
    """Load the Zenodo communities fixture.

    Create extra PID if license is to be mapped and already exists, otherwise
    create a new license record and a PID.
    """
    data = read_json('data/communities.json')
    owner = User.query.filter_by(email=owner_email).one()

    for comm_data in data:
        community_id = comm_data.pop('id')
        user_id = owner.id
        Community.create(community_id, user_id, **comm_data)
    db.session.commit()
