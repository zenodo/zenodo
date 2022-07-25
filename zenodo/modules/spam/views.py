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

"""View for deletion of spam content."""

from __future__ import absolute_import, print_function, unicode_literals

from itertools import islice

from elasticsearch_dsl import Q
from flask import Blueprint, abort, current_app, flash, redirect, \
    render_template, request, url_for
from flask_login import login_required
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access.permissions import Permission
from invenio_accounts.admin import _datastore
from invenio_accounts.models import User
from invenio_communities.models import Community
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_search.api import RecordsSearch

from zenodo.modules.deposit.utils import delete_record
from zenodo.modules.spam.forms import DeleteSpamForm
from zenodo.modules.spam.models import SafelistEntry

blueprint = Blueprint(
    'zenodo_spam',
    __name__,
    url_prefix='/spam',
    template_folder='templates',
)


@blueprint.route('/<int:user_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete(user_id):
    """Delete spam."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    user = User.query.get(user_id)
    deleteform = DeleteSpamForm()
    communities = Community.query.filter_by(id_user=user.id)

    rs = RecordsSearch(index='records').query(
        Q('query_string', query="owners: {0}".format(user.id)))
    rec_count = rs.count()

    ctx = {
        'user': user,
        'form': deleteform,
        'is_new': False,
        'communities': communities,
        'rec_count': rec_count,
    }

    if deleteform.validate_on_submit():

        if deleteform.remove_all_communities.data:
            for c in communities:
                if not c.deleted_at:
                    if not c.description.startswith('--SPAM--'):
                        c.description = '--SPAM--' + c.description
                    if c.oaiset:
                        db.session.delete(c.oaiset)
                    c.delete()
            db.session.commit()
        if deleteform.deactivate_user.data:
            _datastore.deactivate_user(user)
            db.session.commit()
        # delete_record function commits the session internally
        # for each deleted record
        if deleteform.remove_all_records.data:
            for r in rs.scan():
                delete_record(r.meta.id, 'spam', int(current_user.get_id()))

        flash("Spam removed", category='success')
        return redirect(url_for('.delete', user_id=user.id))
    else:
        records = islice(rs.scan(), 10)
        ctx.update(records=records)
        return render_template('zenodo_spam/delete.html', **ctx)

def user_info(owners):
    users = (
        User.query
        .options(db.joinedload(User.profile), db.joinedload(
            User.external_identifiers))
        .filter(User.id.in_(owners))
    )

    data = {}

    for user in users:
        info = {
            "id": user.id,
            "email": user.email,
            "full_name": user.profile.full_name,
            "username": user.profile.username,
            "last_records": "",
            "external_identifiers": "",
        }

        # TODO maybe make it more beautiful?
        try:
            if user.external_identifiers:
                for identifier in user.external_identifiers:
                    info["external_identifiers"] = (
                        info["external_identifiers"] + identifier.method + ", "
                    )
                info["external_identifiers"] = info["external_identifiers"][
                    :-2
                ]
        except Exception:
            pass

        last_records = owners[user.id]['last_records']
        if last_records:
            for record in last_records:
                info["last_records"] = (
                    info["last_records"] + record.title + ", "
                )
            info["last_records"] = info["last_records"][:-2]

        data[user.id] = info

    return data

@blueprint.route('/safelist/admin', methods=['GET'])
@login_required
def safelist_admin():
    """Safelist admin."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    # TODO make time range dynamic
    search = RecordsSearch(index='records')\
        .filter('range' ,  **{'created': {'gte': 'now-4w' , 'lt': 'now'}})\
        .filter('term', _safelisted=False) \

    user_agg = search.aggs.bucket('user', 'terms', field='owners', size=1000)
    user_agg.metric('records', 'top_hits', size=3, _source=['title'])
    res = search[0:0].execute()

    owners = {}
    for user in res.aggregations.user.buckets:
        try:
            if not owners.get(user):
                owner = user.key
                owners[owner] = {
                    'last_records': user.records
                }
        except Exception:
            pass

    users = user_info(owners=owners)

    ctx = {
        'users': users,
    }

    return render_template('zenodo_spam/safelist/admin.html', **ctx)

@blueprint.route('/<int:user_id>/safelist', methods=['POST'])
@login_required
def safelist_add_remove(user_id):
    """Add or remove user from the safelist."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    user = User.query.get(user_id)
    if request.form['action'] == 'post':
        # Create safelist entry
        SafelistEntry.create(user_id=user.id, notes=u'Added by {} ({})'.format(
            current_user.email, current_user.id))

        flash("Added to safelist", category='success')
    else:
        # Remove safelist entry
        SafelistEntry.remove_by_user_id(user.id)
        flash("Removed from safelist", category='warning')

    rs = RecordsSearch(index='records').filter(
        'term', owners=user_id).source(False)
    index_threshold = current_app.config.get(
        'ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD', 1000)
    if rs.count() < index_threshold:
        for record in rs.scan():
            RecordIndexer().index_by_id(record.meta.id)
    else:
        RecordIndexer().bulk_index((
            record.meta.id for record in rs.scan()
        ))

    return redirect(request.form['next'])
