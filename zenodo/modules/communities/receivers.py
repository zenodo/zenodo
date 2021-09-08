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

"""Receivers for Zenodo Communities."""

from __future__ import absolute_import, print_function

from .tasks import dispatch_webhook


def send_inclusion_request_webhook(sender, request=None, **kwargs):
    """Signal receiver to send webhooks after a community inclusion request."""
    dispatch_webhook.delay(
        community_id=str(request.id_community),
        record_id=str(request.id_record),
        event_type='community.records.inclusion',
    )


def send_record_accepted_webhook(
        sender, record=None, community=None, community_id=None, **kwargs):
    """Signal receiver to send webhooks on a record accepted in a community."""
    import ipdb; ipdb.set_trace()
    dispatch_webhook.delay(
        community_id=community_id or str(community.id),
        record_id=str(record.id),
        event_type='community.records.addition',
    )
