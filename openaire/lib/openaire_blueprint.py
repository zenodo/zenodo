# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""OpenAIRE Flask Blueprint"""

from flask import render_template, abort, request, current_app, flash, \
    redirect, url_for, send_file, jsonify, g
import uuid as uuid_mod
import hashlib
from wtforms import Field
from werkzeug import secure_filename
from invenio.bibformat import format_record
from invenio.webinterface_handler_flask_utils import InvenioBlueprint, _
from invenio.webuser_flask import current_user
from invenio.bibdocfile import download_external_url
from invenio.openaire_deposit_engine import get_exisiting_publications_for_uid,\
    OpenAIREPublication
from werkzeug.datastructures import MultiDict
import invenio.template
import os
from invenio.openaire_forms import DepositionForm, DepositionFormMapper, PublicationMapper
import json
from invenio.config import CFG_SITE_SUPPORT_EMAIL, CFG_SITE_NAME
from invenio.usercollection_model import UserCollection


blueprint = InvenioBlueprint('deposit', __name__,
    url_prefix="/deposit",
    breadcrumbs=[
        (_('Upload'), 'deposit.index'),
    ],
    menubuilder=[
        ('main.deposit', _('Upload'), 'deposit.index', 1),
    ],
)

openaire_deposit_templates = invenio.template.load('openaire_deposit')


def is_editable(pub):
    return pub.status in ['initialized', 'edited']


# - Wash url arg
# - check redirect to login on guest
# - check error message for logged in user not authorized


@blueprint.route('/', methods=['GET', 'POST'])
#@blueprint.route('/c/<string:collection>', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_errorpage(template='openaire_error.html', exc_list=(ValueError,))
def index(collection=None):
    """
    Index page with uploader and list of existing depositions
    """
    u = None
    upload_url = url_for('deposit.upload')
    dropbox_upload_url = url_for('deposit.dropbox_upload')

    if 'c' in request.values:
        u = UserCollection.query.get(request.values.get('c'))
        if u:
            upload_url = url_for('deposit.upload', c=u.id)
            dropbox_upload_url = url_for('deposit.dropbox_upload', c=u.id)

    return render_template(
        "openaire_index.html",
        title=_('Upload'),
        myresearch=get_exisiting_publications_for_uid(current_user.get_id()),
        pub=None,
        usercollection=u,
        upload_url=upload_url,
        dropbox_upload_url=dropbox_upload_url,
    )


@blueprint.route('/upload', methods=['POST', 'GET'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_wash_urlargd({'pub_id': (unicode, None)})
def upload(pub_id=None):
    """
    PLUpload backend
    """
    if pub_id:
        pub_id = pub_id.encode('utf8')
    uid = current_user.get_id()

    if 'file' not in request.files:
        abort(400)

    afile = request.files['file']
    filename = secure_filename(afile.filename)
    publication = OpenAIREPublication(uid, publicationid=pub_id)

    # Pre-fill user collection:
    c = request.values.get('c', None)
    if c:
        publication.add_usercollection(c)

    if not is_editable(publication):
        flash("You cannot upload new files when your upload has already been submitted!")
        abort(400)

    publication.add_a_fulltext(None, filename, req_file=afile)

    return publication.publicationid


@blueprint.route('/upload/dropbox', methods=['POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_wash_urlargd({'pub_id': (unicode, None), 'fileurl': (unicode, '')})
def dropbox_upload(pub_id=None, fileurl=''):
    """
    Dropbox upload backend
    """
    if pub_id:
        pub_id = pub_id.encode('utf8')
    if fileurl:
        fileurl = fileurl.encode('utf8')

    uid = current_user.get_id()

    if not fileurl:
        abort(400)

    if not (fileurl.startswith("https://dl.dropbox.com/") or fileurl.startswith("https://dl.dropboxusercontent.com/")):
        abort(400)

    publication = OpenAIREPublication(uid)
    if not is_editable(publication):
        flash("You cannot upload new files when your upload has already been submitted!")
        abort(400)

    # Pre-fill user collection
    c = request.values.get('c', None)
    if c:
        publication.add_usercollection(c)

    uploaded_file = download_external_url(fileurl)
    publication.add_a_fulltext(uploaded_file, secure_filename(os.path.basename(fileurl)))

    return redirect(url_for('deposit.edit', pub_id=publication.publicationid))


@blueprint.route('/getfile/<string:pub_id>/<string:file_id>', methods=['GET'])
@blueprint.route('/getfile/<string:pub_id>/<string:file_id>/<string:action>/', methods=['GET'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
def getfile(pub_id='', file_id='', action='view'):
    """
    View for stream file or deleting it.
    """
    pub_id = pub_id.encode('utf8')
    file_id = file_id.encode('utf8')
    action = action.encode('utf8')

    uid = current_user.get_id()

    if action not in ['view', 'delete']:
        abort(404)

    try:
        pub = OpenAIREPublication(uid, pub_id)
        fulltext = pub.fulltexts[file_id]
    except (ValueError, KeyError):
        abort(404)

    if action == 'view':
        return send_file(fulltext.get_full_path(),
                    attachment_filename=fulltext.get_full_name(),
                    as_attachment=True)
    elif action == 'delete':
        if not is_editable(pub):
            flash("You cannot delete files when your upload has already been submitted!")
            return redirect(url_for('.edit', pub_id=pub.publicationid))
        if len(pub.fulltexts.keys()) > 1:
            if pub.remove_a_fulltext(file_id):
                flash("File was deleted", category='success')
            else:
                flash("File could not be deleted. Please contact support.", category='danger')
        else:
            flash("File cannot be deleted. You must provide minimum one file.")
        return redirect(url_for('.edit', pub_id=pub.publicationid))


@blueprint.route('/check/', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
def check():
    value = request.args.get('value', '')
    field_name = request.args.get('field', '')
    if field_name == "":
        return "{}"

    form = DepositionForm()
    try:
        field = form._fields[field_name]
        field.process(MultiDict({field_name: value}))
        if field.validate(form):
            return json.dumps({"error_message": "", "error": 0})
        else:
            return json.dumps({"error_message": " ".join(field.errors), "error": 1})
    except (KeyError, AttributeError, TypeError), e:
        return json.dumps({"error_message": unicode(e), "error": 0})


@blueprint.route('/autocomplete/', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
def autocomplete():
    """
        Returns a list with of suggestions for the field based on the current value
    """
    field = request.args.get('field')
    term = request.args.get('term')
    try:
        limit = int(request.args.get('limit'))

        if limit > 0:
            form = DepositionForm()
            field = getattr(form, field)
            val = field.autocomplete(term, limit)
            return json.dumps(val)
    except (AttributeError, ValueError):
        pass
    return json.dumps([])


@blueprint.route('/edit/<string:pub_id>/', methods=['GET', 'POST'])
@blueprint.route('/edit/<string:pub_id>/<string:action>/', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_set_breadcrumb('Edit')
def edit(pub_id=u'', action=u'edit'):
    """
    Edit an upload
    """
    uid = current_user.get_id()

    if action not in ['edit', 'save', 'delete', 'reserve-doi']:
        abort(404)

    try:
        pub = OpenAIREPublication(uid, publicationid=pub_id)
        title = pub.metadata.get('title', 'Untitled') or 'Untitled'
        editable = is_editable(pub)
    except ValueError:
        abort(404)

    # All POST requests change the publication, and are not allowed if the
    # publication is not editable anymore.
    if request.method == 'POST':
        if not editable:
            flash("You cannot edit an already submitted upload. Please contact %s if you would like to make changes!" % CFG_SITE_SUPPORT_EMAIL)
            return redirect(url_for('.edit', pub_id=pub.publicationid))

    #
    # Action handling
    #
    ctx = {}
    if action == 'reserve-doi':
        #
        # Reserve DOI action (AjAX)
        #
        if request.method == 'POST':
            doi = pub.create_doi()
            return json.dumps({'doi': doi})
        else:
            abort(405)
    elif action == 'delete':
        #
        # Delete action
        #
        if not editable:
            flash("You cannot delete an already submitted upload. Please contact %s if you would like to have it removed!" % CFG_SITE_SUPPORT_EMAIL)
            return redirect(url_for('.edit', pub_id=pub.publicationid))
        pub.delete()
        flash("Upload '%s' was deleted." % title, 'success')
        return redirect(url_for('.index'))
    elif action == 'edit':
        #
        # Edit action
        #
        upload_url = url_for('deposit.upload', pub_id=pub.publicationid)
        dropbox_upload_url = url_for('deposit.dropbox_upload', pub_id=pub.publicationid)

        ctx = {
            'pub': pub,
            'recid': pub.metadata.get('__recid__', None),
            'title': title,
            'is_editable': editable,
            'upload_url': upload_url,
            'dropbox_upload_url': dropbox_upload_url,
        }

        if request.method == 'POST':
            form = DepositionForm(request.values, crsf_enabled=False)
            mapper = DepositionFormMapper(pub)
            pub = mapper.map(form)
            form._pub = pub

            if form.validate():
                pub.save()
                pub.upload_record()
                flash("Upload was successfully submitted - it may take up 5 minutes before it has been fully integrated into %s." % CFG_SITE_NAME, category='success')
                return redirect(url_for('.index'))
            else:
                pub.save()
                ctx['form'] = form
                ctx['form_message'] = "The form was saved, but there were errors. Please see below."
        elif editable:
            mapper = PublicationMapper()
            form = DepositionForm(mapper.map(pub), crsf_enabled=False)
            ctx['form'] = form
        else:
            ctx['record_hd'] = format_record(recID=pub.recid, xml_record=pub.marcxml, ln=g.ln, of='hd')
            ctx['record_hdinfo'] = format_record(recID=pub.recid, xml_record=pub.marcxml, ln=g.ln, of='HDINFO')

    elif action == 'save':
        #
        # Save action (AjAX)
        #
        if request.method == 'POST':
            form = DepositionForm(request.values, crsf_enabled=False)
            mapper = DepositionFormMapper(pub)
            pub = mapper.map(form)
            form._pub = pub
            if form.validate():
                pub.save()
                return json.dumps({'status': 'success', 'form': 'Successfully saved.'})
            else:
                pub.save()
                errors = dict([(x, '') for x in form._fields.keys()])
                errors.update(form.errors)
                return json.dumps({
                    'status': 'warning',
                    'form': 'The form was saved, but there were errors. Please see below.',
                    'fields': errors,
                })
        else:
            abort(405)

    return render_template(
        "openaire_edit.html",
        myresearch=get_exisiting_publications_for_uid(current_user.get_id()),
        **ctx
    )
