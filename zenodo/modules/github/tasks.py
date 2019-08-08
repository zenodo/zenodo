# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Celery background tasks."""

import arrow
from celery import shared_task
from invenio_db import db
from invenio_github.api import GitHubAPI
from invenio_oauthclient.models import RemoteAccount


@shared_task(ignore_result=True)
def sync_remote_accounts():
    """Sync all remote accounts which haven't been synced in more than several months."""
    # TODO:
    # 1) fetch all Remote Accounts which haven't been synced in the last x months
    # 2) sync the accounts
    remote_accounts = find_not_synced_remote_accounts(1)
    for remote_account in remote_accounts:
        sync_remote_account.delay(remote_account.user_id)


@shared_task(ignore_result=True)
def sync_remote_account(user_id):
    """Sync a remote account."""
    gh_api = GitHubAPI(user_id=user_id)
    gh_api.sync()


def find_not_synced_remote_accounts(month):
    import wdb; wdb.set_trace()
    filtered_remote_accounts = []
    all_remote_accounts = db.session.query(RemoteAccount).all()
    # .filter(RemoteAccount.extra_data['last_sync'] < arrow.utcnow().replace(month=-month))

    for remote_account in all_remote_accounts:
        last_sync = arrow.get(remote_account.extra_data['last_sync'])
        if remote_account.extra_data['last_sync'] and \
            last_sync < arrow.utcnow().replace(months=-month):
                filtered_remote_accounts.append(remote_account)

    return filtered_remote_accounts
