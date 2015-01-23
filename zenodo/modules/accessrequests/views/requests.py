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

from datetime import date

from flask import Blueprint, current_app, request, abort, render_template, \
    flash, url_for, redirect, send_file
from flask_login import current_user

from invenio.base.i18n import _
from invenio.ext.sslify import ssl_required
from invenio.modules.accounts.models import User
from invenio.modules.records.api import get_record
from invenio.modules.records.views import request_record
from invenio.legacy.bibdocfile.api import BibRecDocs, InvenioBibDocFileError


from ..forms import AccessRequestForm
from ..models import AccessRequest, RequestStatus, SecretLink
from ..tokens import EmailConfirmationSerializer

blueprint = Blueprint(
    'zenodo_accessrequests',
    __name__,
    url_prefix="/record",
    static_folder="../static",
    template_folder="../templates",
)

#
# Helpers
#


def get_bibdocfile(bibarchive, filename):
    """Get BibDocFile for."""
    for f in bibarchive.list_latest_files():
        if not f.is_icon() and f.get_full_name() == filename:
            return f
    return None

#
# Template filters
#


@blueprint.app_template_filter(name="is_restricted")
def is_restricted(record):
    return record.get('access_right') == 'restricted' and \
        record.get('access_conditions') and \
        record.get('owner', {}).get('id')


@blueprint.app_template_filter()
def is_embargoed(record):
    return record.get('access_right') == 'embargoed' and \
        record.get('embargo_date') and \
        record.get('embargo_date') > date.today()

#
# Views
#


@blueprint.route('/<int:recid>/accessrequest', methods=['GET', 'POST'])
@ssl_required
@request_record
def access_request(recid=None):
    """Create an access request."""
    record = get_record(recid)

    # Record must be in restricted access mode.
    if record.get('access_right') != 'restricted' or \
       not record.get('access_conditions'):
        abort(404)

    # Record must have an owner and owner must still exists.
    try:
        record_owner = User.query.get_or_404(record['owner']['id'])
    except KeyError:
        abort(404)

    sender = None
    initialdata = dict()

    # Prepare initial form data
    if current_user.is_authenticated():
        sender = current_user
        initialdata = dict(
            # FIXME: add full_name attribute to user accounts.
            full_name=" ".join([sender["family_name"], sender["given_names"]]),
            email=sender["email"],
        )

    # Normal form validation
    form = AccessRequestForm(formdata=request.form, **initialdata)

    if form.validate_on_submit():
        accreq = AccessRequest.create(
            recid=recid,
            receiver=record_owner,
            sender_full_name=form.data['full_name'],
            sender_email=form.data['email'],
            justification=form.data['justification'],
            sender=sender
        )

        if accreq.status == RequestStatus.EMAIL_VALIDATION:
            flash(_(
                "Email confirmation needed: We have sent you an email to "
                "verify your address. Please check the email and follow the "
                "instructions to complete the access request."),
                category='info')
        else:
            flash(_("Access request submitted."), category='info')
        return redirect(url_for("record.metadata", recid=recid))

    return render_template(
        'accessrequests/access_request.html',
        record=record,
        form=form,
    )


@blueprint.route('/<int:recid>/accessrequest/<token>/confirm/',
                 methods=['GET', ])
@ssl_required
@request_record
def confirm(recid=None, token=None):
    """Confirm email address."""
    # Validate token
    data = EmailConfirmationSerializer().validate_token(token)
    if data is None:
        flash(_("Invalid confirmation link."), category='danger')
        return redirect(url_for("record.metadata", recid=recid))

    # Validate request exists.
    r = AccessRequest.query.get(data['id'])
    if not r:
        abort(404)

    # Confirm email address.
    if r.status != RequestStatus.EMAIL_VALIDATION:
        abort(404)

    r.confirm_email()
    flash(_("Email validated and access request submitted."), category='info')

    return redirect(url_for("record.metadata", recid=recid))


@blueprint.route('/<int:recid>/restrictedfiles/<path:filename>',
                 methods=['GET'])
@ssl_required
@request_record
def file(recid=None, filename=None):
    """Serve restricted file for record using provided token.

    This is a simple reimplementation of legacy bibdocfile file serving. Only
    the latest version of a file can be served.
    """
    if not SecretLink.validate_token(request.args.get('token'),
                                     dict(recid=recid)):
        return abort(404)

    try:
        bibarchive = BibRecDocs(recid)
    except InvenioBibDocFileError:
        current_app.logger.warning("File not found.", exc_info=True)
        abort(404)

    if bibarchive.deleted_p():
        abort(410)

    f = get_bibdocfile(bibarchive, filename)

    if f is None:
        abort(404)

    return send_file(f.get_path())
