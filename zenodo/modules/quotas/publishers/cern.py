# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Deposit disk usage metrics per user."""

from __future__ import absolute_import

from cernservicexml import ServiceDocument, XSLSPublisher
from flask import current_app
from werkzeug.utils import import_string

from ..models import Publisher


class CERNPublisher(Publisher):

    """Metrics publisher for CERN XSLS service."""

    @classmethod
    def publish(cls, metrics):
        """Publish service metrics to CERN XSLS service."""
        api_url = current_app.config.get('QUOTAS_XSLS_API_URL')
        service_id = current_app.config.get('QUOTAS_XSLS_SERVICE_ID')

        if api_url is None:
            raise RuntimeError("QUOTAS_XSLS_API_URL must be set.")
        if service_id is None:
            raise RuntimeError("QUOTAS_XSLS_SERVICE_ID must be set.")

        # Create service document.
        doc = ServiceDocument(
            service_id,
            contact=current_app.config.get('CFG_SITE_SUPPORT_EMAIL'),
            webpage=current_app.config.get('CFG_SITE_URL'),
        )

        for obj in metrics:
            doc.add_numericvalue(obj.metric, obj.value)

        # Compute availability
        try:
            avail_imp = current_app.config.get(
                'QUOTAS_XSLS_AVAILABILITY')
            if avail_imp:
                avail_func = import_string(avail_imp)
                doc.status = avail_func(doc)
        except Exception:
            current_app.logger.exception("Could not compute availability")

        resp = XSLSPublisher.send(doc, api_url=api_url)
        if resp.status_code != 200:
            raise RuntimeError("%s did not accept service XML (status %s)" % (
                    resp.content, resp.status_code), resp.content)
