# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo Webhooks API."""

from __future__ import absolute_import, print_function, unicode_literals

import re
import time
import uuid

import requests
from flask import current_app

from .proxies import current_zenodo_webhooks


class Event:
    """Webhook event object."""

    def __init__(self, event_type, source, payload, event_id=None,
                 timestamp=None):
        """Event initialization."""
        self.event_id = event_id or uuid.uuid4()
        self.timestamp = timestamp or time.time()
        self.event_type = event_type
        self.source = source
        self.payload = payload

    @classmethod
    def match_subscribers(cls, event_type):
        """Return subscribers that match the event."""
        matched_subscribers = []
        for subscriber in current_zenodo_webhooks.subscribers:
            # NOTE: Events are usually something like 'relations.citations', or
            # 'relations.*'. The fact that there is a match-any-char-dot ('.'),
            # won't be an issue.
            try:
                if re.match(subscriber['event'], event_type):
                    matched_subscribers.append(subscriber)
            except re.error:
                current_app.logger.warning(
                    'Invalid subscriber event regex: {}'.format(subscriber))
        return matched_subscribers

    @property
    def request_body(self):
        """Return body for an event request."""
        return {
            'id': str(self.event_id),
            'time': self.timestamp,
            'event_type': self.event_type,
            'payload': self.payload,
            'source': self.source,
        }

    @property
    def request_headers(self):
        """Return headers for an event request."""
        # NOTE: Inspired from:
        # - GitHub: https://developer.github.com/webhooks/#delivery-headers
        # - Thorn: http://thorn.readthedocs.io/en/stable/userguide/dispatch.html#http-headers
        return {
            'X-Zenodo-Event': self.event_type,
            # TODO: Include HMAC signature of the body
            # 'X-Hub-Signature': sign(body),
            'X-Zenodo-Delivery': str(self.event_id),
        }

    def send(self, subscriber, sign=False):
        """Send event request to a subscriber."""
        assert subscriber['content_type'] == 'application/json'
        if sign:
            # TODO: Include HMAC signature of the body using
            # subscriber['secret']
            pass
        res = requests.post(
            subscriber['url'],
            json=self.request_body,
            headers=self.request_headers)
        if not res.ok:
            print(
                u'Failed sending {} to {}'.format(self, subscriber['id']))
            raise Exception(
                'Webhook delivery bad response {}'.format(res.text))
        print(
            u'Successfully sent {} to {}'.format(self, subscriber['id']))

    def __repr__(self):
        return (
            u'<Event({self.event_id}, {self.event_type}, {self.timestamp})>'
            .format(self=self))
