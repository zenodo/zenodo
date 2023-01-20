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

"""Notifications models."""
from __future__ import absolute_import

from invenio_db import db
from invenio_webhoks.models import Receiver

from .errors import NotificationAlreadyReceivedError, RecordNotFoundError

from sqlalchemy.dialects import mysql

RELEASE_STATUS_TITLES = {
    'RECEIVED': _('Received'),
    'PROCESSING': _('Processing'),
    'PUBLISHED': _('Published'),
    'FAILED': _('Failed'),
    'DELETED': _('Deleted'),
}

RELEASE_STATUS_ICON = {
    'RECEIVED': 'fa-spinner',
    'PROCESSING': 'fa-spinner',
    'PUBLISHED': 'fa-check',
    'FAILED': 'fa-times',
    'DELETED': 'fa-times',
}

RELEASE_STATUS_COLOR = {
    'RECEIVED': 'default',
    'PROCESSING': 'default',
    'PUBLISHED': 'success',
    'FAILED': 'danger',
    'DELETED': 'danger',
}

class PeerReviewStatus(Enum):
    """Constants for possible status of a Peer Review."""

    __order__ = 'RECEIVED PROCESSING PUBLISHED FAILED DELETED'

    RECEIVED = 'R'
    """Release has been received and is pending processing."""

    PROCESSING = 'P'
    """Release is still being processed."""

    PUBLISHED = 'D'
    """Release was successfully processed and published."""

    FAILED = 'F'
    """Release processing has failed."""

    DELETED = 'E'
    """Release has been deleted."""

    def __init__(self, value):
        """Hack."""

    def __eq__(self, other):
        """Equality test."""
        return self.value == other

    def __str__(self):
        """Return its value."""
        return self.value

    @property
    def title(self):
        """Return human-readable title."""
        return RELEASE_STATUS_TITLES[self.name]

    @property
    def icon(self):
        """Font Awesome status icon."""
        return RELEASE_STATUS_ICON[self.name]

    @property
    def color(self):
        """UI status color."""
        return RELEASE_STATUS_COLOR[self.name]

class PeerReview(db.Model):
    __tablename__ = "notifications_peer_reviews"
    __versioned__ = {"versioning": False}

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    """Peer review identifier."""

    notification_id = db.Column(UUIDType, unique=True, nullable=True)
    """Unique notification identifier."""

    # Example payload here: https://notify.coar-repositories.org/scenarios/8/

    doi_url = db.Column(db.String(255)) # TODO: Make longer?
    # TODO Maybe save the whole cite-as URL value instead?
    """ Peer review DOI """

    origin = db.Column(db.String(255)) # TODO: Make longer?

    errors = db.Column(
        JSONType().with_variant(
            postgresql.JSON(none_as_null=True),
            'postgresql',
        ),
        nullable=True,
    )
    """Peer review processing errors."""

    event_id = db.Column(UUIDType, db.ForeignKey(Event.id), nullable=True)
    """Incoming webhook event identifier."""

    record_id = db.Column(
        UUIDType,
        db.ForeignKey(RecordMetadata.id),
        nullable=True,
    )
    """Record identifier."""

    status = db.Column(
        ChoiceType(PeerReviewStatus, impl=db.CHAR(1)),
        nullable=False,
    )
    """Status of the peer review, e.g. 'processing', 'published', 'failed',
    etc."""

    recordmetadata = db.relationship(RecordMetadata, backref='peer_reviews')
    event = db.relationship(Event)

    @classmethod
    def create(cls, event):
        """Create a new PeerReview model."""
        # Check if the release has already been received
        notification_id = event.payload['id'].split(':')[-1]
        existing_peer_review = PeerReview.query.filter_by(
            notification_id=notification_id,
        ).first()

        if existing_peer_review:
            raise NotificationAlreadyReceivedError(
                notification=existing_peer_review)

        # Create the Peer Review
        context = event.payload['context']
        record_doi = '/'.join(context['ietf:cite-as'].split('/')[-2:])
        origin =  event.payload['origin']['id']

        recid, record = get_record(record_doi)
        if record:
            peer_review = event.payload['object']
            doi_url = peer_review['ietf:cite-as']

            with db.session.begin_nested():
                peer_review = cls(
                    notification_id=notification_id,
                    doi_url=doi_url,
                    origin=origin,
                    event=event,
                    status=ReleaseStatus.RECEIVED,
                )
                db.session.add(peer_review)
            return peer_review
        else:
            raise RecordNotFoundError(doi=record_doi)

    @property
    def record(self):
        """Get Record object."""
        if self.recordmetadata:
            return Record(self.recordmetadata.json, model=self.recordmetadata)
        else:
            return None

    @property
    def deposit_id(self):
        """Get deposit identifier."""
        if self.record and '_deposit' in self.record:
            return self.record['_deposit']['id']
        else:
            return None

    def __repr__(self):
        """Get PeerReview representation."""
        return (u'<PeerReview {self.doi}:{self.notification_id} ({self.status.title})>'
                .format(self=self))

