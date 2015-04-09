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

"""Token serializers."""

import binascii
import os

from base64 import urlsafe_b64encode
from datetime import datetime

from itsdangerous import BadData, JSONWebSignatureSerializer, \
    SignatureExpired, TimedJSONWebSignatureSerializer

from invenio.base.globals import cfg


class TokenMixin(object):

    """Mix-in class for token serializers."""

    def create_token(self, obj_id, extra_data):
        """Create a token referencing the object id with extra data.

        Note random data is added to ensure that no two tokens are identical.
        """
        return self.dumps(dict(id=obj_id, data=extra_data,
                               rnd=binascii.hexlify(os.urandom(4))))

    def validate_token(self, token, expected_data=None):
        """Validate secret link token.

        :param token: Token value.
        :param expected_data: A dictionary of key/values that must be present
            in the data part of the token (i.e. included via ``extra_data`` in
            ``create_token``).
        """
        try:
            # Load token and remove random data.
            data = self.load_token(token)

            # Compare expected data with data in token.
            if expected_data:
                for k in expected_data:
                    if expected_data[k] != data["data"].get(k):
                        return None
            return data
        except BadData:
            return None

    def load_token(self, token, force=False):
        """Load data in a token.

        :param token: Token to load.
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        try:
            data = self.loads(token)
        except SignatureExpired, e:
            if not force:
                raise
            data = e.payload

        del data["rnd"]
        return data


class EncryptedTokenMixIn(TokenMixin):

    """Mix-in class for token serializers that generate encrypted tokens."""

    @property
    def engine(self):
        """Get cryptographic engine."""
        if not hasattr(self, '_engine'):
            from cryptography.fernet import Fernet
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes

            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(cfg['SECRET_KEY'].encode('utf8'))
            fernet_key = urlsafe_b64encode(digest.finalize())
            self._engine = Fernet(fernet_key)
        return self._engine

    def create_token(self, obj_id, extra_data):
        """Create a token referencing the object id with extra data."""
        return self.engine.encrypt(
            super(EncryptedTokenMixIn, self).create_token(obj_id, extra_data)
        )

    def load_token(self, token, force=False):
        """Load data in a token.

        :param token: Token to load.
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        return super(EncryptedTokenMixIn, self).load_token(
            self.engine.decrypt(token), force=force
        )


class EmailConfirmationSerializer(TimedJSONWebSignatureSerializer, TokenMixin):

    """Serializer for email confirmation link tokens.

    Depends upon the secrecy of ``SECRET_KEY``. Tokens expire after a specific
    time (defaults to ``ACCESSREQUESTS_CONFIRMLINK_EXPIRES_IN``). The
    access request id as well as the email address is stored in the token
    together with a random bit to ensure all tokens are unique.
    """

    def __init__(self, expires_in=None):
        """Initialize underlying TimedJSONWebSignatureSerializer."""
        dt = expires_in or cfg['ACCESSREQUESTS_CONFIRMLINK_EXPIRES_IN']

        super(EmailConfirmationSerializer, self).__init__(
            cfg['SECRET_KEY'],
            expires_in=dt,
            salt='accessrequests-email',
        )


class SecretLinkSerializer(JSONWebSignatureSerializer,
                           TokenMixin):

    """Serializer for secret links."""

    def __init__(self):
        """Initialize underlying JSONWebSignatureSerializer."""
        super(SecretLinkSerializer, self).__init__(
            cfg['SECRET_KEY'],
            salt='accessrequests-link',
        )


class TimedSecretLinkSerializer(TimedJSONWebSignatureSerializer,
                                TokenMixin):

    """Serializer for expiring secret links."""

    def __init__(self, expires_at=None):
        """Initialize underlying TimedJSONWebSignatureSerializer."""
        assert isinstance(expires_at, datetime) or expires_at is None

        dt = expires_at - datetime.now() if expires_at else None

        super(TimedSecretLinkSerializer, self).__init__(
            cfg['SECRET_KEY'],
            expires_in=int(dt.total_seconds()) if dt else None,
            salt='accessrequests-timedlink',
        )


class SecretLinkFactory(object):

    """"Functions for creating and validating any secret link tokens."""

    @classmethod
    def create_token(cls, obj_id, data, expires_at=None):
        """Create the secret link token."""
        if expires_at:
            s = TimedSecretLinkSerializer(expires_at=expires_at)
        else:
            s = SecretLinkSerializer()

        return s.create_token(obj_id, data)

    @classmethod
    def validate_token(cls, token, expected_data=None):
        """Validate a secret link token (non-expiring + expiring)."""
        s = SecretLinkSerializer()
        st = TimedSecretLinkSerializer()

        data = st.validate_token(token, expected_data=expected_data)
        if data:
            return data

        return s.validate_token(token, expected_data=expected_data)

    @classmethod
    def load_token(cls, token, force=False):
        """Validate a secret link token (non-expiring + expiring)."""
        s = SecretLinkSerializer()
        st = TimedSecretLinkSerializer()

        try:
            return s.load_token(token, force=force)
        except BadData:
            return st.load_token(token, force=force)
