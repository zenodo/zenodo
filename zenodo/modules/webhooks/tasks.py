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

"""Zenodo webhooks module."""

from __future__ import absolute_import, print_function, unicode_literals

from celery import shared_task
from werkzeug.utils import import_string

from .api import Event


def dispatch_events(events, **kwargs):
    for event_type, payload in events.items():
        publish_event.delay(event_type, payload=payload, **kwargs)


# FIXME: Refactor this to use some Event generator registry...
@shared_task(ignore_result=True)
def generate_events(generator_import_path, generator_kwargs, **kwargs):
    """Generates webhook events."""
    event_generator = import_string(generator_import_path)
    events = event_generator(**generator_kwargs)
    dispatch_events(events, **kwargs)


@shared_task(ignore_result=True)
def publish_event(event_type, **kwargs):
    """Publish events to webhook subscribers."""
    for subscriber in Event.match_subscribers(event_type):
        send_event_request.delay(subscriber, event_type=event_type, **kwargs)


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=60)
def send_event_request(subscriber, **kwargs):
    """Send event request to subscriber."""
    try:
        Event(**kwargs).send(subscriber)
    except Exception as exc:
        send_event_request.retry(exc=exc)
