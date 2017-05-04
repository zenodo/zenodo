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
from invenio_pidstore.models import PersistentIdentifier

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.utils import fetch_depid
from zenodo.modules.records.api import ZenodoRecord


def get_github_repository(pid):
    """Get GitHub repository from depid."""
    depid = fetch_depid(pid)
    # First check if the passed depid is a GitHub release
    release = (Release.query.filter_by(record_id=depid.object_uuid)
               .one_or_none())
    if release:
        return release.repository

    deposit = ZenodoDeposit.get_record(depid.object_uuid)
    concepterecid = deposit.get('conceptrecid')
    if not concepterecid:
        return None
    parent = PersistentIdentifier.get(
        pid_type='recid', pid_value=concepterecid)
    pv = PIDVersioning(parent=parent)
    if pv.exists:
        record_ids = [r.object_uuid for r in pv.children]
        deposit_ids = (rec.depid.object_uuid
                       for rec in ZenodoRecord.get_records(record_ids))
        release = (Release.query
                   .filter(Release.record_id.in_(deposit_ids))
                   .first())
        return release.repository if release else None


def is_github_versioned(pid):
    """Return true if the pid is part of a GitHub repository versioning."""
    depid = fetch_depid(pid)
    return get_github_repository(depid)


def is_github_owner(user, pid, sync=False):
    """Return true if the user can create a new version for a GitHub record.

    :param user: User to check for ownership.
    :param pid: pid of a record.
    :param sync: Condition to sync the user's repository info from GitHub.
    """
    depid = fetch_depid(pid)
    if sync:
        try:
            commit = False
            with db.session.begin_nested():
                gh = GitHubAPI(user_id=user.id)
                if gh.account and gh.check_sync():
                    gh.sync(hooks=False)
                    commit = True
            if commit:
                db.session.commit()
        except Exception:
            # TODO: Log a warning?
            # TODO: (In case GitHub is down, we still want to render the page)
            pass
    repo = get_github_repository(depid)
    return repo.user == user if repo else False
