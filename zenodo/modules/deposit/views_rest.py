# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017, 2019 CERN.
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

"""Redirects for legacy URLs."""

from __future__ import absolute_import, print_function

from functools import wraps

from flask import Blueprint, abort, jsonify, request
from flask.views import MethodView
from flask_principal import ActionNeed
from flask_security import login_required
from invenio_access import Permission
from invenio_db import db
from invenio_files_rest import current_files_rest
from invenio_files_rest.models import ObjectVersion
from invenio_records_rest.views import pass_record

from ..records.permissions import deposit_update_permission_factory
from .extra_formats import ExtraFormats
from .scopes import extra_formats_scope
from .utils import suggest_language

blueprint = Blueprint(
    'zenodo_deposit',
    __name__,
    url_prefix='',
)


@blueprint.route(
    '/language/',
    methods=['GET']
)
@login_required
def language():
    """Suggest a language on the deposit form."""
    q = request.args.get('q', '')
    limit = int(request.args.get('limit', '5').lower())
    langs = suggest_language(q, limit=limit)
    langs = [{'code': l.alpha_3, 'name': l.name} for l in langs]
    d = {
        'suggestions': langs
    }
    return jsonify(d)


def pass_extra_formats_mimetype(from_query_string=None, from_content_type=None,
                                from_accept=None):
    """Decorator to validate the request's extra formats MIMEType."""
    assert from_content_type or from_accept or from_query_string

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            mimetype = None
            if from_query_string:
                mimetype = request.args.get('mimetype')
            if not mimetype and from_content_type:
                mimetype = request.headers.get('Content-Type')
            if not mimetype and from_accept:
                mimetype = next((m for m, _ in request.accept_mimetypes), None)
            if mimetype not in ExtraFormats.mimetype_whitelist:
                abort(400, '"{}" is not an acceptable MIMEType.'
                      .format(mimetype))
            return f(self, *args, mimetype=mimetype, **kwargs)
        return inner
    return decorator


def extra_formats_scope_permission():
    """Helper function to check the existence of extra_formats_scope."""
    if getattr(request, 'oauth', None) is not None:
        token_scopes = set(request.oauth.access_token.scopes)
        return extra_formats_scope.id in token_scopes
    return False


def check_extra_formats_permission(f):
    """Extra formats permission decorator."""
    @wraps(f)
    def decorator(self, record=None, *args, **kwargs):
        if Permission(ActionNeed('admin-access')) or \
             (deposit_update_permission_factory(record=record).can() and
              extra_formats_scope_permission()):
            return f(self, record=record, *args, **kwargs)
        abort(403)
    return decorator


class DepositExtraFormatsResource(MethodView):
    """Deposit extra formats resource."""

    @pass_extra_formats_mimetype(from_query_string=True, from_accept=True)
    @pass_record
    @check_extra_formats_permission
    def get(self, pid, record, mimetype=None, **kwargs):
        """Get an extra format."""
        depid, deposit = pid, record  # this is a deposit endpoint
        if mimetype in deposit.extra_formats:
            fileobj = deposit.extra_formats[mimetype]
            return fileobj.obj.send_file(trusted=True)
        return abort(404, 'No extra format "{}".'.format(mimetype))

    @pass_extra_formats_mimetype(from_content_type=True)
    @pass_record
    @check_extra_formats_permission
    def put(self, pid, record, mimetype=None, **kwargs):
        """Create or replace an extra format."""
        depid, deposit = pid, record  # this is a deposit endpoint
        stream, content_length, content_md5 = \
            current_files_rest.upload_factory()
        with db.session.begin_nested():
            extra_formats_bucket = ExtraFormats.get_or_create_bucket(deposit)

            # Link bucket to published record if needed
            if deposit.is_published():
                recid, record = deposit.fetch_published()
                ExtraFormats.link_to_record(record, extra_formats_bucket)

            obj = ObjectVersion.create(
                extra_formats_bucket, mimetype, mimetype=mimetype)
            obj.set_contents(
                stream,
                size=content_length,
                size_limit=extra_formats_bucket.size_limit)
        db.session.commit()

        return jsonify({
            'message': 'Extra format "{}" updated.'.format(mimetype)
        })

    @pass_extra_formats_mimetype(from_content_type=True)
    @pass_record
    @check_extra_formats_permission
    def delete(self, pid, record, mimetype=None, **kwargs):
        """Delete an extra format."""
        depid, deposit = pid, record  # this is a deposit endpoint
        if mimetype in deposit.extra_formats:
            del deposit.extra_formats[mimetype]
        db.session.commit()
        return jsonify({
            'message': 'Extra format "{}" deleted.'.format(mimetype)})

    @pass_record
    @check_extra_formats_permission
    def options(self, pid, record, **kwargs):
        """Get a list of all extra formats."""
        depid, deposit = pid, record  # this is a deposit endpoint
        if deposit.extra_formats:
            return jsonify(deposit.extra_formats.dumps())
        else:
            return jsonify([])


class RecordExtraFormatsResource(MethodView):
    """Record extra formats resource."""

    # NOTE: No permissions (allow all)
    # this is considered record metadata (not files)
    @pass_extra_formats_mimetype(from_query_string=True, from_accept=True)
    @pass_record
    def get(self, pid, record, mimetype=None, **kwargs):
        """Get extra format."""
        if mimetype in record.extra_formats:
            fileobj = record.extra_formats[mimetype]
            return fileobj.obj.send_file(trusted=True)
        return abort(404, 'No extra format "{}".'.format(mimetype))

    # NOTE: No permissions (allow all),
    # this is considered extra_formats (not files)
    @pass_record
    def options(self, pid, record, **kwargs):
        """Get available extra formats."""
        if record.extra_formats:
            return jsonify(record.extra_formats.dumps())
        else:
            return jsonify([])


_DEPID = 'pid(depid,record_class="zenodo.modules.deposit.api:ZenodoDeposit")'
_RECID = 'pid(recid,record_class="zenodo.modules.records.api:ZenodoRecord")'

blueprint.add_url_rule(
    '/deposit/depositions/<{}:pid_value>/formats'.format(_DEPID),
    view_func=DepositExtraFormatsResource.as_view('depid_extra_formats'),
)

blueprint.add_url_rule(
    '/records/<{}:pid_value>/formats'.format(_RECID),
    view_func=RecordExtraFormatsResource.as_view('recid_extra_formats'),
)
