# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2023 CERN.
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

"""Notifications tasks."""
from __future__ import absolute_import

from celery import shared_task
from invenio_db import db

from .errors import InvalidSenderError
from .models import PeerReview, PeerReviewStatus
from .proxies import current_notifications

@shared_task(ignore_result=True, max_retries=5, default_retry_delay=10 * 60)
def process_peer_review(notification_id, verify_sender=False):
    """Process a received PeerReview."""
    peer_review = PeerReview.query.filter(
        PeerReview.notification_id == notification_id,
        PeerReview.status.in_([PeerReviewStatus.RECEIVED,
                               PeerReviewStatus.FAILED]),
    ).one()

    if verify_sender and not peer_review.verify_sender():
        peer_review.status = PeerReviewStatus.FAILED
        raise InvalidSenderError(
            event=peer_review.event.id, user=peer_review.event.user_id)

    peer_review.status = PeerReviewStatus.PUBLISHED
    db.session.commit()
