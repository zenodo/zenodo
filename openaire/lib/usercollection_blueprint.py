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

from flask import render_template, abort, request, flash, \
    redirect, url_for
from invenio.webinterface_handler_flask_utils import InvenioBlueprint, _
from invenio.webuser_flask import current_user
from invenio.usercollection_forms import CollectionForm, EditCollectionForm, \
    DeleteCollectionForm
from invenio.usercollection_model import UserCollection
from invenio.sqlalchemyutils import db


blueprint = InvenioBlueprint(
    'usercollection',
    __name__,
    url_prefix="/collections",
    breadcrumbs=[
        (_('User Collections'), 'usercollection.index'),
    ],
    menubuilder=[
        ('main.usercollection', _('Collections'), 'usercollection.index', 1),
    ],
)


def mycollections_ctx(uid):
    """
    Helper method for return ctx used by many views
    """
    return {
        'mycollections': UserCollection.query.filter_by(
            id_user=uid).order_by(db.asc(UserCollection.title)).all()
    }


@blueprint.route('/', methods=['GET', ])
def index():
    """
    Index page with uploader and list of existing depositions
    """
    uid = current_user.get_id()
    ctx = mycollections_ctx(uid)
    ctx.update({
        'title': _('Collections'),
        'usercollections': UserCollection.query.order_by(UserCollection.title).all(),
    })

    return render_template(
        "usercollection_index.html",
        **ctx
    )


@blueprint.route('/<string:usercollection_id>/', methods=['GET'])
def detail(usercollection_id=None):
    """
    Index page with uploader and list of existing depositions
    """
    # Check existence of collection
    u = UserCollection.query.filter_by(id=usercollection_id).first_or_404()
    uid = current_user.get_id()

    ctx = mycollections_ctx(uid)
    ctx.update({
        'is_owner': u.id_user == uid,
        'usercollection': u,
    })

    return render_template(
        "usercollection_detail.html",
        **ctx
    )


@blueprint.route('/new/', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_set_breadcrumb('Create new')
def new():
    """
    Create or edit a collection.
    """
    uid = current_user.get_id()
    form = CollectionForm(request.values, crsf_enabled=False)

    ctx = mycollections_ctx(uid)
    ctx.update({
        'form': form,
        'is_new': True,
        'usercollection': None,
    })

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        data['id'] = data['identifier']
        del data['identifier']
        u = UserCollection(id_user=uid, **data)
        db.session.add(u)
        db.session.commit()
        u.save_collections()
        flash("Collection was successfully created.", category='success')
        return redirect(url_for('.index'))

    return render_template(
        "usercollection_new.html",
        **ctx
    )


@blueprint.route('/edit/<string:usercollection_id>/', methods=['GET', 'POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_set_breadcrumb('Edit')
def edit(usercollection_id):
    """
    Create or edit a collection.
    """
    # Check existence of collection
    u = UserCollection.query.filter_by(id=usercollection_id).first_or_404()
    uid = current_user.get_id()

    # Check ownership
    if u.id_user != uid:
        abort(404)

    form = EditCollectionForm(request.values, u, crsf_enabled=False)
    deleteform = DeleteCollectionForm()
    ctx = mycollections_ctx(uid)
    ctx.update({
        'form': form,
        'is_new': False,
        'usercollection': u,
        'deleteform': deleteform,
    })

    if request.method == 'POST' and form.validate():
        for field, val in form.data.items():
            setattr(u, field, val)
        db.session.commit()
        u.save_collections()
        flash("Collection successfully edited.", category='success')
        return redirect(url_for('.edit', usercollection_id=u.id))

    return render_template(
        "usercollection_new.html",
        **ctx
    )


@blueprint.route('/delete/<string:usercollection_id>/', methods=['POST'])
@blueprint.invenio_force_https
@blueprint.invenio_authenticated
@blueprint.invenio_authorized('submit', doctype='ZENODO')
@blueprint.invenio_set_breadcrumb('Delete')
def delete(usercollection_id):
    """
    Delete a collection
    """
    # Check existence of collection
    u = UserCollection.query.filter_by(id=usercollection_id).first_or_404()
    uid = current_user.get_id()

    # Check ownership
    if u.id_user != uid:
        abort(404)

    deleteform = DeleteCollectionForm(request.values)
    ctx = mycollections_ctx(uid)
    ctx.update({
        'deleteform': deleteform,
        'is_new': False,
        'usercollection': u,
    })

    if request.method == 'POST' and deleteform.validate():
        u.delete_collections()
        db.session.delete(u)
        db.session.commit()
        flash("Collection was successfully deleted.", category='success')
        return redirect(url_for('.index'))
    else:
        flash("Collection could not be deleted.", category='warning')
        return redirect(url_for('.edit', usercollection_id=u.id))
