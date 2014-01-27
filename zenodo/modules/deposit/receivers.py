# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from flask import request, current_app

from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.fields.file_upload import FileUploadField
from invenio.modules.deposit.field_widgets import PLUploadWidget
from invenio.modules.deposit.models import DepositionDraftCacheManager


class UploadForm(WebDepositForm):
    plupload_file = FileUploadField(
        label="",
        widget=PLUploadWidget(
            template="deposit/widget_plupload_index.html"
        )
    )


def index_context_listener(sender, context=None):
    """
    Add extra variables into deposit index template to create
    """
    if context:
        context['form'] = UploadForm()
        context['deposition_type'] = None

        if 'c' in request.values:
            try:
                from invenio.modules.communities.models import Community
                c = Community.query.get(request.values.get('c'))

                draft_cache = DepositionDraftCacheManager.get()
                draft_cache.data['communities'] = [{
                    'identifier': c.id,
                    'title': c.title,
                }, ]
                del draft_cache.data['c']
                draft_cache.save()
                current_app.logger.info(draft_cache.data)
                context['community'] = c
            except Exception:
                context['community'] = None
            except ImportError:
                # Community module not installed
                pass


def large_file_notification(sender, deposition=None, deposition_file=None,
                            **kwargs):
    """
    Send notification on large file uploads
    """
    if deposition_file and deposition_file.size > 10485760:
        from invenio.mailutils import send_email
        from invenio.config import CFG_SITE_ADMIN_EMAIL, CFG_SITE_NAME
        from invenio.textutils import nice_size
        from invenio.jinja2utils import render_template_to_string
        current_app.logger.info(deposition_file.__getstate__())
        send_email(
            CFG_SITE_ADMIN_EMAIL,
            CFG_SITE_ADMIN_EMAIL,
            subject="%s: %s file uploaded" % (
                CFG_SITE_NAME, nice_size(deposition_file.size)
            ),
            content=render_template_to_string(
                "deposit/email_large_file.html",
                deposition=deposition,
                deposition_file=deposition_file,
            )
        )
