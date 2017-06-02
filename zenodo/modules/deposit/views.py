# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

from datetime import datetime
from functools import wraps

from elasticsearch.exceptions import NotFoundError
from flask import Blueprint, abort, current_app, flash, redirect, \
    render_template, request, url_for
from flask_babelex import gettext as _
from flask_security import current_user, login_required
from invenio_communities.models import Community
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records_files.models import RecordsBuckets

from zenodo.modules.deposit.utils import delete_record
from zenodo.modules.records.permissions import record_permission_factory

from .api import ZenodoDeposit
from .fetchers import zenodo_deposit_fetcher
from .forms import RecordDeleteForm
from .tasks import datacite_inactivate, datacite_register

blueprint = Blueprint(
    'zenodo_deposit',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


@blueprint.errorhandler(PIDDeletedError)
def tombstone_errorhandler(error):
    """Render tombstone page."""
    return render_template(
        current_app.config['RECORDS_UI_TOMBSTONE_TEMPLATE'],
        pid=error.pid,
        record=error.record or {},
    ), 410


def pass_record(action, deposit_cls=ZenodoDeposit):
    """Pass record and deposit record to function."""
    def decorator(f):
        @wraps(f)
        def inner(pid_value):
            # Resolve pid_value to record pid and record
            pid, record = pid_value.data

            # Check permissions.
            permission = record_permission_factory(
                record=record, action=action)
            if not permission.can():
                abort(403)

            # Fetch deposit id from record and resolve deposit record and pid.
            depid = zenodo_deposit_fetcher(None, record)
            if not depid:
                abort(404)

            depid, deposit = Resolver(
                pid_type=depid.pid_type,
                object_type='rec',
                getter=deposit_cls.get_record,
            ).resolve(depid.pid_value)

            return f(pid=pid, record=record, depid=depid, deposit=deposit)
        return inner
    return decorator


@login_required
def legacy_index():
    """Legacy deposit."""
    c_id = request.args.get('c', type=str)
    if c_id:
        return redirect(url_for('invenio_deposit_ui.new', c=c_id))
    return render_template(current_app.config['DEPOSIT_UI_INDEX_TEMPLATE'])


@login_required
def new():
    """Create a new deposit."""
    c = Community.get(request.args.get('c', type=str))
    return render_template(current_app.config['DEPOSIT_UI_NEW_TEMPLATE'],
                           record={'_deposit': {'id': None}}, community=c)


@blueprint.route(
    '/record/<pid(recid,record_class='
    '"zenodo.modules.records.api:ZenodoRecord"):pid_value>',
    methods=['POST']
)
@login_required
@pass_record('update')
def edit(pid=None, record=None, depid=None, deposit=None):
    """Edit a record."""
    # If the record doesn't have a DOI, its deposit shouldn't be editable.
    if 'doi' not in record:
        abort(404)

    # Put deposit in edit mode if not already.
    if deposit['_deposit']['status'] != 'draft':
        deposit = deposit.edit()
        db.session.commit()

    return redirect(url_for(
        'invenio_deposit_ui.{0}'.format(depid.pid_type),
        pid_value=depid.pid_value
    ))


@blueprint.route(
    '/record/<pid(recid,record_class='
    '"zenodo.modules.records.api:ZenodoRecord"):pid_value>'
    '/newversion',
    methods=['POST']
)
@login_required
@pass_record('newversion')
def newversion(pid=None, record=None, depid=None, deposit=None):
    """Create a new version of a record."""
    # If the record doesn't have a DOI, its deposit shouldn't be editable.
    if 'doi' not in record:
        abort(404)

    # FIXME: Maybe this has to go inside the API (`ZenodoDeposit.newversion`)
    # If this is not the latest version, get the latest and extend it
    latest_pid = PIDVersioning(child=pid).last_child
    if pid != latest_pid:
        # We still want to do a POST, so we specify a 307 reidrect code
        return redirect(url_for('zenodo_deposit.newversion',
                                pid_value=latest_pid.pid_value), code=307)

    deposit.newversion()
    db.session.commit()

    new_version_deposit = PIDVersioning(child=pid).draft_child_deposit

    return redirect(url_for(
        'invenio_deposit_ui.{0}'.format(new_version_deposit.pid_type),
        pid_value=new_version_deposit.pid_value
    ))


@blueprint.route(
    '/record/<pid(recid,record_class='
    '"zenodo.modules.records.api:ZenodoRecord"):pid_value>'
    '/registerconceptdoi',
    methods=['POST']
)
@login_required
@pass_record('registerconceptdoi')
def registerconceptdoi(pid=None, record=None, depid=None, deposit=None):
    """Register the Concept DOI for the record."""
    # If the record doesn't have a DOI, its deposit shouldn't be editable.
    if 'conceptdoi' in record:
        abort(404)  # TODO: Abort with better code if record is versioned

    deposit.registerconceptdoi()
    db.session.commit()

    return redirect(url_for('invenio_records_ui.recid',
                    pid_value=pid.pid_value))


@blueprint.route(
    '/record'
    '/<pid(recid,record_class='
    '"zenodo.modules.records.api:ZenodoRecord"):pid_value>'
    '/admin/delete',
    methods=['GET', 'POST']
)
@login_required
@pass_record('delete')
def delete(pid=None, record=None, depid=None, deposit=None):
    """Delete a record."""
    # View disabled until properly implemented and tested.
    try:
        doi = PersistentIdentifier.get('doi', record['doi'])
    except PIDDoesNotExistError:
        doi = None

    pids = [pid, depid, doi]
    if 'conceptdoi' in record:
        conceptdoi = PersistentIdentifier.get('doi', record['conceptdoi'])
        pids.append(conceptdoi)
    else:
        conceptdoi = None

    if 'conceptrecid' in record:
        conceptrecid = PersistentIdentifier.get('recid',
                                                record['conceptrecid'])
        pids.append(conceptrecid)
    else:
        conceptrecid = None

    form = RecordDeleteForm()
    form.standard_reason.choices = current_app.config['ZENODO_REMOVAL_REASONS']
    if form.validate_on_submit():
        reason = form.reason.data or dict(
            current_app.config['ZENODO_REMOVAL_REASONS']
        )[form.standard_reason.data]
        delete_record(record.id, reason, int(current_user.get_id()))
        flash(
            _('Record %(recid)s and associated objects successfully deleted.',
                recid=pid.pid_value),
            category='success'
        )
        return redirect(url_for('zenodo_frontpage.index'))
    return render_template(
        'zenodo_deposit/delete.html',
        form=form,
        pid=pid,
        pids=pids,
        record=record,
        deposit=deposit,
    )


@blueprint.app_context_processor
def current_datetime():
    """Template contex processor which adds current datetime to the context."""
    now = datetime.utcnow()
    return {
        'current_datetime': now,
        'current_date': now.date(),
        'current_time': now.time(),
    }


@blueprint.app_template_filter('tolinksjs')
def to_links_js(pid, deposit=None):
    """Get API links."""
    if not isinstance(deposit, ZenodoDeposit):
        return []

    self_url = current_app.config['DEPOSIT_RECORDS_API'].format(
        pid_value=pid.pid_value)
    links = {
        'self': self_url,
        'html': url_for(
            'invenio_deposit_ui.{}'.format(pid.pid_type),
            pid_value=pid.pid_value),
        'bucket': current_app.config['DEPOSIT_FILES_API'] + '/{0}'.format(
            str(deposit.files.bucket.id)),
        'discard': self_url + '/actions/discard',
        'edit': self_url + '/actions/edit',
        'publish': self_url + '/actions/publish',
        'newversion': self_url + '/actions/newversion',
        'registerconceptdoi': self_url + '/actions/registerconceptdoi',
        'files': self_url + '/files',
    }

    # Add versioning links
    conceptrecid = deposit.get('conceptrecid')
    if conceptrecid:
        conceptrecid = PersistentIdentifier.get('recid', conceptrecid)
        pv = PIDVersioning(parent=conceptrecid)
        latest_record = pv.last_child
        if latest_record:
            links['latest'] = current_app.config['RECORDS_API'].format(
                pid_value=latest_record.pid_value)
            links['latest_html'] = url_for(
                'invenio_records_ui.recid', pid_value=latest_record.pid_value)
        draft_child_depid = pv.draft_child_deposit
        if draft_child_depid:
            links['latest_draft'] = (
                current_app.config['DEPOSIT_RECORDS_API']
                .format(pid_value=draft_child_depid.pid_value))
            links['latest_draft_html'] = url_for(
                'invenio_deposit_ui.{}'.format(draft_child_depid.pid_type),
                pid_value=draft_child_depid.pid_value)
    return links


@blueprint.app_template_filter('tofilesjs')
def to_files_js(deposit):
    """List files in a deposit."""
    if not isinstance(deposit, ZenodoDeposit):
        return []

    res = []

    for f in deposit.files:
        res.append({
            'key': f.key,
            'version_id': f.version_id,
            'checksum': f.file.checksum,
            'size': f.file.size,
            'completed': True,
            'progress': 100,
            'links': {
                'self': (
                    current_app.config['DEPOSIT_FILES_API'] +
                    u'/{bucket}/{key}?versionId={version_id}'.format(
                        bucket=f.bucket_id,
                        key=f.key,
                        version_id=f.version_id,
                    )),
            }
        })

    for f in deposit.multipart_files.all():
        res.append({
            'key': f.key,
            'size': f.size,
            'multipart': True,
            'completed': f.completed,
            'processing': True,
            'progress': 100,
            'links': {
                'self': (
                    current_app.config['DEPOSIT_FILES_API'] +
                    u'/{bucket}/{key}?uploadId={upload_id}'.format(
                        bucket=f.bucket_id,
                        key=f.key,
                        upload_id=f.upload_id,
                    )),
            }
        })

    return res
