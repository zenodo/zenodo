# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2021 CERN.
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

"""Tasks for Zenodo Communities."""

from __future__ import absolute_import, print_function

import uuid
from copy import deepcopy
from datetime import datetime

import requests
from celery import shared_task
from flask import current_app
from invenio_communities.models import Community

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.serializers import json_v1


@shared_task(ignore_results=True)
def dispatch_webhook(community_id, record_id, event_type):
    """Build webhook payload and dispatch delivery tasks."""
    webhooks_cfg = current_app.config.get('ZENODO_COMMUNITIES_WEBHOOKS', {})
    recipients = webhooks_cfg.get(community_id, [])
    if not recipients:
        return

    # TODO: Extract to a utility?
    record = ZenodoRecord.get_record(record_id)
    community = Community.query.get(community_id)
    record_payload = json_v1.transform_record(record.pid, record)
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "context": {
            "community": community.id,
            "user": record['owners'][0],
        },
        "payload": {
            "community": {
                "id": community.id,
                "owner": {
                    "id": community.id_user,
                }
            },
            "record": record_payload,
        },
    }
    for recipient_id in recipients:
        deliver_webhook.delay(payload, community_id, recipient_id)


@shared_task(ignore_result=True, max_retries=3, default_retry_delay=10 * 60)
def deliver_webhook(payload, community_id, recipient_id):
    """Deliver the webhook payload to a recipient."""
    try:
        webhooks_cfg = current_app.config.get(
            'ZENODO_COMMUNITIES_WEBHOOKS', {})
        recipient_cfg = deepcopy(webhooks_cfg.get(community_id, {}).get(recipient_id))
        if recipient_cfg:
            recipient_cfg.setdefault('headers', {})
            recipient_cfg['headers'].update({
                # TODO: Make configurable
                'User-Agent': 'Zenodo v3.0.0',
            })
            res = requests.post(json=payload, **recipient_cfg)
            res.raise_for_status()
    except Exception as exc:
        deliver_webhook.retry(exc=exc)
