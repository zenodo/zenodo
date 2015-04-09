# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Database models for shared links."""

from __future__ import absolute_import

from datetime import date, datetime

from flask import url_for
from sqlalchemy_utils.types import ChoiceType, EncryptedType

from invenio.base.globals import cfg
from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db
from invenio.modules.accounts.models import User


from .errors import InvalidRequestStateError
from .receivers import connect_receivers
from .signals import link_created, link_revoked, request_accepted, \
    request_confirmed, request_created, request_rejected
from .tokens import SecretLinkFactory


class RequestStatus(object):

    """Access request status representation."""

    EMAIL_VALIDATION = u'C'
    PENDING = u'P'
    ACCEPTED = u'A'
    REJECTED = u'R'


class SecretLink(db.Model):

    """Represent a secret link to a record restricted files."""

    __tablename__ = 'accreqLINK'

    id = db.Column(db.Integer(unsigned=True), primary_key=True,
                   autoincrement=True)
    """Secret link id."""

    token = db.Column(EncryptedType(db.Text, lambda: cfg['SECRET_KEY']),
                      nullable=False)
    """Secret token for link (should be stored encrypted)."""

    owner_user_id = db.Column(
        db.Integer(unsigned=True), db.ForeignKey(User.id),
        nullable=False, default=None
    )
    """Owner's user id."""

    owner = db.relationship(User, foreign_keys=[owner_user_id])
    """Relationship to user"""

    created = db.Column(db.DateTime, nullable=False, default=datetime.now,
                        index=True)
    """Creation timestamp."""

    expires_at = db.Column(db.DateTime, nullable=True)
    """Expiration date."""

    revoked_at = db.Column(db.DateTime, nullable=True, index=True)
    """Creation timestamp."""

    title = db.Column(db.String(length=255), nullable=False, default='')
    """Title of link."""

    description = db.Column(db.Text, nullable=False, default='')
    """Description of link."""

    @classmethod
    def create(cls, title, owner, extra_data, description="", expires_at=None):
        """Create a new secret link."""
        if isinstance(expires_at, date):
            expires_at = datetime.combine(expires_at, datetime.min.time())

        obj = cls(
            owner=owner,
            title=title,
            description=description,
            expires_at=expires_at,
            token="",
        )
        db.session.add(obj)
        db.session.commit()
        # Create token (dependent on obj.id and recid)
        obj.token = SecretLinkFactory.create_token(
            obj.id, extra_data, expires_at=expires_at
        )
        db.session.commit()
        link_created.send(obj)
        return obj

    @classmethod
    def validate_token(cls, token, expected_data):
        """Validate a secret link token.

        Only queries the database if token is valid to determine that the token
        has not been revoked.
        """
        data = SecretLinkFactory.validate_token(
            token, expected_data=expected_data
        )

        if data:
            link = cls.query.get(data['id'])
            if link and link.is_valid():
                return True
        return False

    @classmethod
    def query_by_owner(cls, user):
        """Get secret links by user."""
        return cls.query.filter_by(
            owner_user_id=user.get_id()
        )

    @property
    def extra_data(self):
        """Load token data stored in token (ignores expiry date of tokens)."""
        if self.token:
            return SecretLinkFactory.load_token(self.token, force=True)["data"]
        return None

    def get_absolute_url(self, endpoint):
        """Get absolute for secret link (using https scheme).

        The endpoint is passed to ``url_for`` with ``token`` and ``extra_data``
        as keyword arguments. E.g.::

            >>> link.extra_data
            dict(recid=1)
            >>> link.get_absolute_url('record.metadata')

        translates into::

            >>> url_for('record.metadata', token="...", recid=1, )
        """
        return url_for(
            endpoint, token=self.token, _external=True, _scheme="https",
            **(self.extra_data or {})
        )

    def revoke(self):
        """Revoken a secret link."""
        if self.revoked_at is None:
            self.revoked_at = datetime.now()
            db.session.commit()
            link_revoked.send(self)
            return True
        return False

    def is_expired(self):
        """Determine if link is expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def is_revoked(self):
        """Determine if link is revoked."""
        return self.revoked_at is not None

    def is_valid(self):
        """Determine if link is still valid."""
        return not(self.is_expired() or self.is_revoked())


class AccessRequest(db.Model):

    """Represent an request for access to restricted files in a record."""

    __tablename__ = 'accreqREQUEST'

    STATUS_CODES = {
        RequestStatus.EMAIL_VALIDATION: _(u'Email validation'),
        RequestStatus.PENDING: _(u'Pending'),
        RequestStatus.ACCEPTED: _(u'Accepted'),
        RequestStatus.REJECTED: _(u'Rejected'),
    }

    id = db.Column(db.Integer(unsigned=True), primary_key=True,
                   autoincrement=True)
    """Access request ID."""

    status = db.Column(
        ChoiceType(STATUS_CODES.items(), impl=db.CHAR(1)),
        nullable=False, index=True
    )
    """Status of request."""

    receiver_user_id = db.Column(
        db.Integer(unsigned=True), db.ForeignKey(User.id),
        nullable=False, default=None
    )
    """Receiver's user id."""

    receiver = db.relationship(User, foreign_keys=[receiver_user_id])
    """Relationship to user"""

    sender_user_id = db.Column(
        db.Integer(unsigned=True), db.ForeignKey(User.id),
        nullable=True, default=None
    )
    """Sender's user id (for authenticated users)."""

    sender = db.relationship(User, foreign_keys=[sender_user_id])
    """Relationship to user for a sender"""

    sender_full_name = db.Column(db.String(length=255), nullable=False,
                                 default='')
    """Sender's full name."""

    sender_email = db.Column(db.String(length=255), nullable=False,
                             default='')
    """Sender's email address."""

    recid = db.Column(db.Integer(unsigned=True), nullable=False, index=True)
    """Record concerned for the request."""

    created = db.Column(db.DateTime, nullable=False, default=datetime.now,
                        index=True)
    """Creation timestamp."""

    modified = db.Column(db.DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)
    """Last modification timestamp."""

    justification = db.Column(db.Text, default='', nullable=False)
    """Sender's justification for how they fulfill conditions."""

    message = db.Column(db.Text, default='', nullable=False)
    """Receivers message to the sender."""

    link_id = db.Column(
        db.Integer(unsigned=True), db.ForeignKey(SecretLink.id),
        nullable=True, default=None
    )
    """Relation to secret link if request was accepted."""

    link = db.relationship(SecretLink, foreign_keys=[link_id])
    """Relationship to secret link."""

    @classmethod
    def create(cls, recid=None, receiver=None, sender_full_name=None,
               sender_email=None, justification=None, sender=None):
        """Create a new access request.

        :param recid: Record id (required).
        :param receiver: User object of receiver (required).
        :param sender_full_name: Full name of sender (required).
        :param sender_email: Email address of sender (required).
        :param justification: Justification message (required).
        :param sender: User object of sender (optional).
        """
        sender_user_id = None if sender is None else sender.get_id()

        assert recid
        assert receiver
        assert sender_full_name
        assert sender_email
        assert justification

        # Determine status
        status = RequestStatus.EMAIL_VALIDATION
        if sender and sender.is_confirmed():
            status = RequestStatus.PENDING

        # Create object
        obj = cls(
            status=status,
            recid=recid,
            receiver_user_id=receiver.get_id(),
            sender_user_id=sender_user_id,
            sender_full_name=sender_full_name,
            sender_email=sender_email,
            justification=justification
        )

        db.session.add(obj)
        db.session.commit()

        # Send signal
        if obj.status == RequestStatus.EMAIL_VALIDATION:
            request_created.send(obj)
        else:
            request_confirmed.send(obj)
        return obj

    @classmethod
    def query_by_receiver(cls, user):
        """Get access requests for a specific receiver."""
        return cls.query.filter_by(
            receiver_user_id=user.get_id()
        )

    @classmethod
    def get_by_receiver(cls, request_id, user):
        """Get access request for a specific receiver."""
        return cls.query.filter_by(
            id=request_id,
            receiver_user_id=user.get_id()
        ).first()

    def confirm_email(self):
        """Confirm that senders email is valid."""
        if self.status != RequestStatus.EMAIL_VALIDATION:
            raise InvalidRequestStateError(RequestStatus.EMAIL_VALIDATION)
        self.status = RequestStatus.PENDING
        db.session.commit()
        request_confirmed.send(self)

    def accept(self, message=None, expires_at=None):
        """Accept request."""
        if self.status != RequestStatus.PENDING:
            raise InvalidRequestStateError(RequestStatus.PENDING)
        self.status = RequestStatus.ACCEPTED
        db.session.commit()
        request_accepted.send(self, message=message, expires_at=expires_at)

    def reject(self, message=None):
        """Reject request."""
        if self.status != RequestStatus.PENDING:
            raise InvalidRequestStateError(RequestStatus.PENDING)
        self.status = RequestStatus.REJECTED
        db.session.commit()
        request_rejected.send(self, message=message)

    def create_secret_link(self, title, description=None, expires_at=None):
        """Create a secret link from request."""
        self.link = SecretLink.create(
            title,
            self.receiver,
            extra_data=dict(recid=self.recid),
            description=description,
            expires_at=expires_at,
        )
        db.session.commit()
        return self.link


#
# Connect signals with receivers
#
connect_receivers()
