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

from invenio_accounts.models import User
from invenio_communities.models import Community
from invenio_communities.utils import save_and_validate_logo
from invenio_db import db

from .utils import file_stream


def loadcommunity(comm_data):
    """Load the Zenodo communities fixture."""
    logo_path = comm_data.pop('logo', None)
    community_id = comm_data.pop('id')
    owner_email = comm_data.pop('owner_email')
    owner_id = User.query.filter_by(email=owner_email).one().id
    c = Community.create(community_id, owner_id, **comm_data)
    if logo_path:
        logo = file_stream(logo_path)
        ext = save_and_validate_logo(logo, logo.name, community_id)
        c.logo_ext = ext
    db.session.commit()
