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
from flask import Blueprint, abort, flash, jsonify, redirect, \
    render_template, request, url_for
from flask_login import login_required
from flask_menu import current_menu
from flask_principal import ActionNeed
from flask_security import current_user
from invenio_access.permissions import Permission
from invenio_accounts.models import User
from invenio_accounts.proxies import current_accounts
from invenio_admin.views import _has_admin_access
from invenio_communities.models import Community
from invenio_db import db
from invenio_search.api import RecordsSearch

from zenodo.modules.deposit.utils import delete_record
from zenodo.modules.spam.forms import DeleteSpamForm
from zenodo.modules.spam.models import SafelistEntry
from zenodo.modules.spam.tasks import delete_spam_user, reindex_user_records

blueprint = Blueprint(
    'zenodo_spam',
    __name__,
    url_prefix='/spam',
    template_folder='templates',
)


@blueprint.before_app_first_request
def init_menu():
    """Initialize menu before first request."""
    # Register safelisting menu entry
    item = current_menu.submenu("settings.safelisting")
    item.register(
        "zenodo_spam.safelist_admin",
        '<i class="fa fa-check fa-fw"></i> Safelisting',
        visible_when=_has_admin_access,
        order=110,
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
            current_accounts.datastore.deactivate_user(user)
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


def _expand_users_info(results):
    """Return user information."""
    user_data = (
        User.query.options(
            db.joinedload(User.profile),
            db.joinedload(User.external_identifiers)
        ).filter(User.id.in_(results.keys()))
    )

    for user in user_data:
        r = results[user.id]
        r.update({
            "id": user.id,
            "email": user.email,
            "external": [i.method for i in (user.external_identifiers or [])]
        })
        if user.profile:
            r.update({
                "full_name": user.profile.full_name,
                "username": user.profile.username,
            })


@blueprint.route('/safelist/admin', methods=['GET'])
@login_required
def safelist_admin():
    """Safelist admin."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    weeks = request.args.get('weeks', 4, type=int)
    # TODO make time range dynamic
    search = RecordsSearch(index='records').filter(
        'range' , **{'created': {'gte': 'now-{}w'.format(weeks) , 'lt': 'now'}}
    ).filter(
        'term', _safelisted=False,
    )

    user_agg = search.aggs.bucket('user', 'terms', field='owners', size=1000)
    user_agg.metric('records', 'top_hits', size=3, _source=['title'])
    res = search[0:0].execute()

    result = {}
    for user in res.aggregations.user.buckets:
        result[user.key] = {
            'last_records': ", ".join(r.title for r in user.records)
        }
    _expand_users_info(result)

    return render_template('zenodo_spam/safelist/admin.html', users=result)


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
    db.session.commit()

    reindex_user_records.delay(user_id)
    return redirect(request.form['next'])

@blueprint.route('/safelist/add/bulk', methods=['POST'])
@login_required
def safelist_bulk_add():
    """Add users to the safelist in bulk."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    user_ids = request.form.getlist('user_ids[]')
    for user_id in user_ids:
        user = User.query.get(user_id)
        SafelistEntry.create(user_id=user.id, notes=u'Added by {} ({})'.format(
            current_user.email, current_user.id))
    db.session.commit()

    for user_id in user_ids:
        reindex_user_records.delay(user_id)

    return jsonify({'message': 'Bulk safelisted'})


@blueprint.route('/delete/bulk', methods=['POST'])
@login_required
def spam_delete_bulk():
    """Delete spam users in bulk."""
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    for user_id in request.form.getlist('user_ids[]'):
        delete_spam_user.delay(user_id, int(current_user.id))
    return jsonify({'message': 'Bulk safelisted'})
