# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Utilities for GitHub management."""

from __future__ import absolute_import, print_function

from invenio_db import db
from invenio_github.api import GitHubAPI
from invenio_github.models import Release
from invenio_pidrelations.contrib.versioning import PIDVersioning


def get_github_release(recid):
    """Get GitHub release from recid."""
    return Release.query.filter_by(record_id=recid.object_uuid).one_or_none()


def get_github_repository(recid):
    """Get GitHub repository from recid."""
    # First check if the passed recid is a GitHub release
    recid_gh_release = get_github_release(recid)
    if recid_gh_release:
        return recid_gh_release.repository

    # Check for its siblings then, in case it was a manual deposit
    pv = PIDVersioning(child=recid)
    if pv.exists:
        # TODO: Maybe a join query might be more efficient...
        for r in pv.children:
            gh_release = get_github_release(r)
            if get_github_release(r):
                return gh_release.repository


def is_github_versioned(recid):
    """Return true if the record is part of a GitHub repository versioning."""
    pv = PIDVersioning(child=recid)
    if pv.exists:
        return any(get_github_release(r) for r in pv.children)


def is_github_owner(user, recid, sync=False):
    """Return true if the user can create a new version for a GitHub record.

    :param user: User to check for ownership.
    :param recid: Recid of a record.
    :param sync: Condition to sync the user's repository info from GitHub.
    """
    if sync:
        with db.session.begin_nested():
            gh = GitHubAPI(user_id=user.id)
            if gh.check_sync():
                gh.sync(hooks=False)
        db.session.commit()
    repo = get_github_repository(recid)
    return repo.user == user
