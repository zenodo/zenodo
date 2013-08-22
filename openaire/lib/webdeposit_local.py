# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
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

from invenio.webdeposit_form import WebDepositForm
from invenio.webdeposit_load_fields import fields
from invenio.webdeposit_field_widgets import PLUploadWidget
from invenio.webdeposit_models import DepositionDraftCacheManager
from invenio.usercollection_model import UserCollection
from flask import request


class UploadForm(WebDepositForm):
    plupload_file = fields.FileUploadField(
        label="",
        widget=PLUploadWidget(
            template="webdeposit_widget_plupload_index.html"
        )
    )


def index_context_listener(sender, context=None):
    if context:
        context['form'] = UploadForm()
        context['deposition_type'] = None

        if 'c' in request.values:
            try:
                u = UserCollection.query.get(request.values.get('c'))

                draft_cache = DepositionDraftCacheManager.get()
                draft_cache.data['communities'] = [{
                    'identifier': u.id,
                    'title': u.title,
                }, ]
                del draft_cache.data['c']
                draft_cache.save()
                from flask import current_app
                current_app.logger.info(draft_cache.data)
                context['usercollection'] = u
            except Exception:
                context['usercollection'] = None

        from flask import current_app
        current_app.logger.info(context)
