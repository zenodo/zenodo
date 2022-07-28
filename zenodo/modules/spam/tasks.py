# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2020 CERN.
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

"""Forms for spam deletion module."""

from __future__ import absolute_import, print_function

from celery import shared_task
from flask import current_app
from invenio_communities.models import Community
from invenio_records.models import RecordMetadata
from invenio_accounts.models import User
from invenio_search.api import RecordsSearch
from invenio_accounts.proxies import current_accounts
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from zenodo.modules.spam import current_spam



@shared_task(ignore_result=False)
def check_metadata_for_spam(community_id=None, dep_id=None):
    """Checks metadata of the provided deposit for spam content."""
    if not current_app.config.get('ZENODO_SPAM_MODEL_LOCATION'):
        return 0
    if community_id:
        community = Community.query.get(community_id)
        spam_proba = current_spam.model.predict_proba(
            [community.title + ' ' + community.description])[0][1]
    if dep_id:
        deposit = RecordMetadata.query.get(dep_id)
        spam_proba = current_spam.model.predict_proba(
            [deposit.json['title'] + ' ' + deposit.json['description']])[0][1]

    return spam_proba


@shared_task(ignore_result=False)
def delete_spam_user(user_id, deleted_by):
    """Deletes a user and marks their records and communities as spam."""
    from zenodo.modules.deposit.utils import delete_record

    user = User.query.get(user_id)
    communities = Community.query.filter_by(id_user=user.id)
    rs = RecordsSearch(index='records').filter('term', owners=user.id)

    for c in communities:
        if not c.deleted_at:
            if not c.description.startswith('--SPAM--'):
                c.description = '--SPAM--' + c.description
            if c.oaiset:
                db.session.delete(c.oaiset)
            c.delete()
    current_accounts.datastore.deactivate_user(user)
    db.session.commit()
    for r in rs.scan():
        delete_record(r.meta.id, 'spam', deleted_by)


@shared_task(ignore_result=False)
def reindex_user_records(user_id):
    """Reindex a user's records."""
    rs = RecordsSearch(index='records').filter(
        'term', owners=user_id).source(False)
    indexer = RecordIndexer()
    index_threshold = current_app.config.get(
        'ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD', 1000)
    if rs.count() < index_threshold:
        for record in rs.scan():
            indexer.index_by_id(record.meta.id)
    else:
        indexer.bulk_index((
            record.meta.id for record in rs.scan()
        ))
