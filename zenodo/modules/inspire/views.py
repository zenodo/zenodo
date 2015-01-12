# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2014 CERN.
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


"""
INSPIRE webhook endpoint
"""

from __future__ import absolute_import

from flask import Blueprint, current_app

from invenio.modules.webhooks.models import Receiver, CeleryReceiver
from ..tasks import handle_inspire_payload


blueprint = Blueprint(
    'zenodo_inspire',
    __name__,
)


#
# Before first request loaders
#
@blueprint.before_app_first_request
def register_webhook():
    """
    Setup webhook endpoint for github notifications
    """
    Receiver.register(
        current_app.config.get('INSPIRE_WEBHOOK_RECEIVER_ID'),
        CeleryReceiver(handle_inspire_payload)
    )
