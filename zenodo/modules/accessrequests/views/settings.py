# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Accounts settings views for pending access requests and shared links."""

from __future__ import absolute_import

import re

from flask import Blueprint, abort, flash, redirect, render_template, \
    request, url_for
from flask_breadcrumbs import register_breadcrumb
from flask_login import current_user, login_required
from flask_menu import register_menu
from jinja2 import Markup, escape, evalcontextfilter

from invenio.base.i18n import _
from invenio.ext.sslify import ssl_required
from invenio.modules.records.api import get_record

from ..forms import ApprovalForm, DeleteForm
from ..helpers import QueryOrdering
from ..models import AccessRequest, RequestStatus, SecretLink


blueprint = Blueprint(
    'zenodo_accessrequests_settings',
    __name__,
    url_prefix="/account/settings/sharedlinks",
    static_folder="../static",
    template_folder="../templates",
)


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@blueprint.app_template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    """Template filter to convert newlines to <br>-tags."""
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@blueprint.route("/", methods=['GET', 'POST'])
@ssl_required
@login_required
@register_menu(
    blueprint, 'settings.sharedlinks',
    _('%(icon)s Shared links', icon='<i class="fa fa-share fa-fw"></i>'),
    order=9,
    active_when=lambda: request.endpoint.startswith(
        "zenodo_accessrequests_settings.")
)
@register_breadcrumb(
    blueprint, 'breadcrumbs.settings.sharedlinks', _('Shared links')
)
def index():
    """List pending access requests and shared links."""
    query = request.args.get('query', '')
    order = request.args.get('sort', '-created')
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except (TypeError, ValueError):
        abort(404)

    # Delete form
    form = DeleteForm(request.form)
    if form.validate_on_submit():
        link = SecretLink.query_by_owner(current_user).filter_by(
            id=form.link.data).first()
        if link.revoke():
            flash(_("Shared link revoked."), category='success')

    # Links
    links = SecretLink.query_by_owner(current_user).filter(
        SecretLink.revoked_at == None
    )

    # Querying
    if query:
        lquery = "%{0}%".format(query)
        links = links.filter(
            SecretLink.title.like(lquery) | SecretLink.description.like(lquery)
        )

    # Ordering
    ordering = QueryOrdering(links, ['title', 'created', 'expires_at'], order)
    links = ordering.items()

    # Pending access requests
    requests = AccessRequest.query_by_receiver(current_user).filter_by(
        status=RequestStatus.PENDING).order_by('created')

    return render_template(
        "accessrequests/settings/index.html",
        links_pagination=links.paginate(page, per_page=per_page),
        requests=requests,
        query=query,
        order=ordering,
        get_record=get_record,
        form=DeleteForm(),
    )


@blueprint.route("/accessrequest/<int:request_id>/", methods=['GET', 'POST'])
@ssl_required
@login_required
@register_breadcrumb(
    blueprint, 'breadcrumbs.settings.sharedlinks.accessrequest',
    _('Access request')
)
def accessrequest(request_id):
    """Accept/reject access request."""
    r = AccessRequest.get_by_receiver(request_id, current_user)
    if not r or r.status != RequestStatus.PENDING:
        abort(404)

    form = ApprovalForm(request.form)

    if form.validate_on_submit():
        if form.accept.data:
            r.accept(message=form.data['message'],
                     expires_at=form.expires_at.data)
            flash(_("Request accepted."))
            return redirect(url_for(".index"))
        elif form.reject.data:
            r.reject(message=form.data['message'])
            flash(_("Request rejected."))
            return redirect(url_for(".index"))

    return render_template(
        "accessrequests/settings/request.html",
        accessrequest=r,
        record=get_record(r.recid),
        form=form,
    )
