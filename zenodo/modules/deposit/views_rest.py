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

from flask import Blueprint, abort, current_app, jsonify, request
from flask.views import MethodView
from flask_security import login_required
from invenio_db import db
from invenio_deposit.scopes import write_scope
from invenio_deposit.utils import check_oauth2_scope
from invenio_files_rest import current_files_rest
from invenio_files_rest.models import ObjectVersion
from invenio_records_rest.views import pass_record

from ..records.permissions import deposit_read_permission_factory, \
    deposit_update_permission_factory
from .api import ZenodoDeposit
from .scopes import metadata_read_scope, metadata_write_scope
from .utils import suggest_language, unlocked_bucket

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


def _mimetype_whitelist():
    return current_app.config['ZENODO_DERIVED_METADATA_MIMETYPE_WHITELIST']


def _metadata_key_prefix():
    return current_app.config['ZENODO_METAFILE_KEY_PREFIX']


def _metadata_file_key(mimetype):
    prefix = current_app.config['ZENODO_METAFILE_KEY_PREFIX']
    return '{}{}'.format(prefix, mimetype)


def validate_metadata_mimetype(f):
    """Decorator to validate the mimetype."""
    @wraps(f)
    def inner(self, *args, **kwargs):
        mimetype = request.view_args['mimetype']
        if mimetype not in _mimetype_whitelist():
            abort(400, '"{}" is not an acceptable mimetype.'.format(mimetype))
        return f(self, *args, **kwargs)
    return inner


read_permission = check_oauth2_scope(
    lambda record: deposit_read_permission_factory(record=record).can(),
    write_scope.id, metadata_read_scope.id)

update_permission = check_oauth2_scope(
    lambda record: deposit_update_permission_factory(record=record).can(),
    write_scope.id, metadata_write_scope.id)


METAFILE_PERMISSIONS = {
    'read': read_permission,
    'update': update_permission,
}


def check_deposit_permission(action):
    """Deposit permission decorator."""
    def _permission_builder(f):
        @wraps(f)
        def decorator(self, record=None, *args, **kwargs):
            if not METAFILE_PERMISSIONS[action](record=record).can():
                abort(403)
            return f(self, record=record, *args, **kwargs)
        return decorator
    return _permission_builder


class DepositMetadataListResource(MethodView):
    """Deposit metadata list resource."""

    @pass_record
    @check_deposit_permission('read')
    def get(self, pid, record, **kwargs):
        """Get a list of all metadata."""
        metadata_files = (f for f in record.files
                          if f['key'].startswith(_metadata_key_prefix()))
        # TODO: expose file information...
        return jsonify({
            f.key.replace(_metadata_key_prefix(), ''): f.file.size
            for f in metadata_files
        })


class DepositMetadataResource(MethodView):
    """Deposit metadata resource."""

    @validate_metadata_mimetype
    @pass_record
    @check_deposit_permission('read')
    def get(self, pid, record, mimetype, **kwargs):
        """Get metadata."""
        key = _metadata_file_key(mimetype)
        if key in record.files:
            fileobj = record.files[key]
            return fileobj.obj.send_file(trusted=True)  # XXX: DANGER-ZONE
        return abort(
            404, 'No metadata exists for the mimetype "{}".'.format(mimetype))

    @validate_metadata_mimetype
    @pass_record
    @check_deposit_permission('update')
    def put(self, pid, record, mimetype, **kwargs):
        """Create or replace metadata."""
        stream, content_length, content_md5 = \
            current_files_rest.upload_factory()

        with unlocked_bucket(record.files.bucket) as bucket:
            with db.session.begin_nested():
                key = _metadata_file_key(mimetype)
                obj = ObjectVersion.create(bucket, key, mimetype=mimetype)
                obj.set_contents(
                    stream, size=content_length, size_limit=bucket.size_limit)
        db.session.commit()

        return jsonify({
            'message': 'Metadata for mimetype "{}" updated.'.format(mimetype)
        })

    @validate_metadata_mimetype
    @pass_record
    @check_deposit_permission('update')
    def delete(self, pid, record, mimetype, **kwargs):
        """Delete metadata."""
        key = _metadata_file_key(mimetype)
        with unlocked_bucket(record.files.bucket):
            if key in record.files:
                del record.files[key]
        db.session.commit()
        return jsonify({
            'message': 'Metadata for mimetype "{}" deleted.'.format(mimetype)})


class RecordMetadataResource(MethodView):
    """Record metadata resource."""

    # NOTE: No permissions (allow all), this is considered metadata (not files)
    @pass_record
    def get(self, pid, record, **kwargs):
        """Get metadata."""
        # Check querystring first, and then "Accept" header
        mimetype = (request.args.get('mimetype') or
                    next((m for m, _ in request.accept_mimetypes), None))
        if mimetype not in _mimetype_whitelist():
            abort(400, '"{}" is not an acceptable mimetype.'.format(mimetype))
        key = _metadata_file_key(mimetype)
        deposit = ZenodoDeposit.get_record(record.depid.object_uuid)
        if key in deposit.files:
            # FIXME: review this!
            # check_record_permission()
            fileobj = deposit.files[key]
            return fileobj.obj.send_file(trusted=True)  # XXX: DANGER-ZONE
        return abort(
            404, 'No metadata exists for the mimetype "{}".'.format(mimetype))

    # NOTE: No permissions (allow all), this is considered metadata (not files)
    @pass_record
    def options(self, pid, record, **kwargs):
        """Get avaiable metadata."""
        deposit = ZenodoDeposit.get_record(record.depid.object_uuid)
        metadata_files = [f.key.replace(_metadata_key_prefix(), '')
                          for f in deposit.files
                          if f['key'].startswith(_metadata_key_prefix())]
        return jsonify(metadata_files)


_DEPID = 'pid(depid,record_class="zenodo.modules.deposit.api:ZenodoDeposit")'
_RECID = 'pid(recid,record_class="zenodo.modules.records.api:ZenodoRecord")'
deposit_base_path = (
    '/deposit/depositions/<{}:pid_value>/metadata'.format(_DEPID))

blueprint.add_url_rule(
    deposit_base_path,
    view_func=DepositMetadataListResource.as_view('depid_metadata_list'),
)

blueprint.add_url_rule(
    '{}/<path:mimetype>'.format(deposit_base_path),
    view_func=DepositMetadataResource.as_view('depid_metadata_item'),
)

blueprint.add_url_rule(
    '/records/<{}:pid_value>/metadata'.format(_RECID),
    view_func=RecordMetadataResource.as_view('recid_metadata'),
)
