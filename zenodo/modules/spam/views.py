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

from collections import Counter
from datetime import datetime, timedelta
from itertools import islice

from elasticsearch_dsl import Q
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, \
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
import sqlalchemy as sa

from zenodo.modules.deposit.utils import delete_record
from zenodo.modules.spam.forms import DeleteSpamForm
from zenodo.modules.spam.models import SafelistEntry
from zenodo.modules.spam.proxies import current_domain_forbiddenlist, \
    current_domain_safelist
from zenodo.modules.spam.tasks import delete_spam_user, reindex_user_records
from zenodo.modules.spam.utils import is_user_safelisted

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
            SafelistEntry.remove_by_user_id(user.id)
            db.session.commit()
        # delete_record function commits the session internally
        # for each deleted record
        if deleteform.remove_all_records.data:
            record_ids = [record.meta.id for record in rs.scan()]
            for record_id in record_ids:
                delete_record(record_id, 'spam', int(current_user.get_id()))

        flash("Spam removed", category='success')
        return redirect(url_for('.delete', user_id=user.id))
    else:
        records = islice(rs.scan(), 10)
        ctx.update(records=records)
        return render_template('zenodo_spam/delete.html', **ctx)


def _normalize_email(email):
    email = email.lower()
    username, domain = email.rsplit("@", 1)
    no_dots_username = username.replace(".", "")

    if domain == "googlemail.com":
        domain = "gmail.com"
    return no_dots_username + "@" + domain


def _get_domain(email):
    return email[email.index("@") :].lower()


def _evaluate_user_domain(email, normalized_emails, email_domain_count):
    email_domain = _get_domain(email)
    is_flagged_domain = email_domain in ["@gmail.com"]
    is_above_threshold = normalized_emails.get(_normalize_email(email), 0) > 3

    domain_counts = email_domain_count[email_domain[1:]]
    domain_info = {
        'domain': email_domain[1:],
        'active_count': domain_counts['active'],
        'total_count': domain_counts['total'],
    }
    if current_domain_forbiddenlist.matches(email_domain):
        domain_info['status'] = "forbidden"
        return domain_info
    if is_flagged_domain and is_above_threshold:
        domain_info['status'] = "forbidden"
        return domain_info
    if current_domain_safelist.matches(email_domain):
        domain_info['status'] = "safe"
        return domain_info
    domain_info['status'] = "unclear"
    return domain_info


def _expand_users_info(results, include_pending=False):
    """Return user information."""
    user_data = (
        User.query.options(
            db.joinedload(User.profile),
            db.joinedload(User.external_identifiers),
            db.joinedload(User.safelist),
        ).filter(User.id.in_(results.keys()))
    )

    normalized_emails = Counter([
        _normalize_email(user.email)
        for user in user_data
    ])

    email_domain_expr = sa.func.split_part(sa.func.lower(User.email), '@', 2)
    email_domains = db.session.query(
        email_domain_expr,
        sa.func.count(User.id),
        sa.func.count(User.id).filter(User.active == True)
    ).group_by(email_domain_expr).all()

    email_domain_count = {
        domain: {'active': active, 'total': total}
        for domain, total, active in email_domains
    }

    for user in user_data:
        is_safelisted = user.safelist
        is_inactivated = not user.active
        if (is_safelisted or is_inactivated) and not include_pending:
            results.pop(user.id)
            continue

        r = results[user.id]
        r.update({
            "id": user.id,
            "email": user.email,
            "external": [i.method for i in (user.external_identifiers or [])],
            "domain_info": _evaluate_user_domain(user.email, normalized_emails,
                                          email_domain_count),
            "active": user.active,
            "safelist": user.safelist,
        })
        if user.profile:
            r.update({
                "full_name": user.profile.full_name,
                "username": user.profile.username
            })


@blueprint.route('/safelist/admin', methods=['GET'])
@login_required
def safelist_admin():
    """Safelist admin."""
    # Only admin can access this view
    if not Permission(ActionNeed('admin-access')).can():
        abort(403)

    data = request.args.get('data', 'all', type=str)
    data_categories = {
        'records': data in ('all', 'records'),
        'communities': data in ('all', 'communities'),
    }
    from_weeks = request.args.get('from_weeks', 4, type=int)
    to_weeks = request.args.get('to_weeks', 0, type=int)
    max_users = request.args.get('max_users', 1000, type=int)
    include_pending = \
        request.args.get('include_pending', 'include', type=str) == 'include'

    result = {}
    if data_categories['records']:
        search = RecordsSearch(index='records').filter(
            'range', **{'created': {'gte': 'now-{}w'.format(from_weeks),
                                    'lt': 'now-{}w'.format(to_weeks)}}
        ).filter(
            'term', _safelisted=False,
        )

        user_agg = search.aggs.bucket('user', 'terms', field='owners',
                                      size=max_users)
        user_agg.metric('records', 'top_hits', size=3, _source=['title',
                                                                'description',
                                                                'recid'])
        res = search[0:0].execute()

        for user in res.aggregations.user.buckets:
            result[user.key] = {
                'last_content_titles': ", ".join(r.title for r in user.records),
                'last_content_descriptions': ", ".join(r.description for r in
                                                       user.records),
                'first_content_url': url_for('invenio_records_ui.recid',
                                             pid_value=user.records[0].recid),
                'total_content': user.doc_count
            }

    if data_categories['communities']:
        from_date = datetime.utcnow() - timedelta(weeks=from_weeks)
        to_date = datetime.utcnow() - timedelta(weeks=to_weeks)

        community_users = db.session.query(
            User.id.label('user_id'),
            sa.func.count(Community.id).label('count'),
            sa.func.max(Community.id).label('c_id'),
            sa.func.max(Community.title).label('title'),
            sa.func.max(Community.description).label('description')
        ).join(Community).group_by(User.id).filter(
            Community.created.between(from_date, to_date),
            Community.deleted_at.is_(None),
            ~User.safelist.any()
        ).limit(max_users)

        for row in community_users:

            user_data = result.get(row.user_id, {
                'last_content_titles': '',
                'last_content_descriptions': '',
                'first_content_url': '',
                'total_content': 0
            })

            if user_data['last_content_titles']:
                user_data['last_content_titles'] += ', '
            user_data['last_content_titles'] += row.title

            if user_data['last_content_descriptions']:
                user_data['last_content_descriptions'] += ', '
            user_data['last_content_descriptions'] += row.description

            user_data['first_content_url'] = url_for('invenio_communities.detail',
                                                     community_id=row.c_id)
            user_data['total_content'] += row.count
            result[row.user_id] = user_data

    _expand_users_info(result, include_pending)

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
        user.active = True
        try:
            if not user.safelist:
                SafelistEntry.create(user_id=user.id,
                                     notes=u'Added by {} ({})'.format(
                                         current_user.email, current_user.id))
        except Exception:
            pass
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

    user_ids = request.form.getlist('user_ids[]')
    for user_id in user_ids:
        user = User.query.get(user_id)
        current_accounts.datastore.deactivate_user(user)
    db.session.commit()

    for user_id in user_ids:
        delete_spam_user.delay(user_id, int(current_user.id))

    return jsonify({'message': 'Bulk safelisted'})
