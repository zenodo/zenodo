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

"""Token creation and validation test case."""

from __future__ import absolute_import

from datetime import datetime, timedelta

from itsdangerous import BadData, BadSignature, JSONWebSignatureSerializer, \
    SignatureExpired

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

from zenodo.modules.accessrequests.tokens import EmailConfirmationSerializer, \
    EncryptedTokenMixIn, SecretLinkFactory, SecretLinkSerializer, \
    TimedSecretLinkSerializer


class EmailConfirmationSerializerTestCase(InvenioTestCase):

    """Test case for email link token."""

    extra_data = dict(email="info@invenio-software.org")

    def test_create_validate(self):
        """Test token creation."""
        s = EmailConfirmationSerializer()
        t = s.create_token(1, self.extra_data)
        data = s.validate_token(t, expected_data=self.extra_data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['data'], dict(email="info@invenio-software.org"))

    def test_expired(self):
        """Test token expiry."""
        s = EmailConfirmationSerializer(expires_in=-20)
        t = s.create_token(1, self.extra_data)
        self.assertIsNone(s.validate_token(t))
        self.assertIsNone(s.validate_token(t, expected_data=self.extra_data))
        self.assertRaises(SignatureExpired, s.load_token, t)
        self.assertIsNotNone(s.load_token(t, force=True))

    def test_expected_data_mismatch(self):
        """Test token validation."""
        s = EmailConfirmationSerializer()
        t = s.create_token(1, self.extra_data)
        self.assertIsNotNone(s.validate_token(t))
        self.assertIsNone(s.validate_token(t, dict(notvalid=1)))
        self.assertIsNone(s.validate_token(t, dict(email='another@email')))

    def test_creation(self):
        """Ensure that no two tokens are identical."""
        s = EmailConfirmationSerializer()
        t1 = s.create_token(1, self.extra_data)
        t2 = s.create_token(1, self.extra_data)
        self.assertNotEqual(t1, t2)


class SecretLinkSerializerTestCase(InvenioTestCase):

    """Test case for email link token."""

    def test_create_validate(self):
        """Test token creation."""
        s = SecretLinkSerializer()
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t)
        self.assertEqual(data['id'], 1234)
        self.assertEqual(data['data']['recid'], 56789)

    def test_creation(self):
        """Ensure that no two tokens are identical."""
        s = SecretLinkSerializer()
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        self.assertNotEqual(t1, t2)

    def test_noencryption(self):
        """Test that token is not encrypted."""
        s = SecretLinkSerializer()
        t1 = s.create_token(1, dict(recid=1))
        self.assertRaises(
            BadSignature,
            JSONWebSignatureSerializer('anotherkey').loads,
            t1
        )


class EncryptedTokenMixinTestCase(InvenioTestCase):

    """Test case for encrypted tokens."""

    class TestSerializer(EncryptedTokenMixIn, SecretLinkSerializer):
        pass

    def test_create_validate(self):
        """Test token creation."""
        s = self.TestSerializer()
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t)
        self.assertEqual(data['id'], 1234)
        self.assertEqual(data['data']['recid'], 56789)

    def test_creation(self):
        """Ensure that no two tokens are identical."""
        s = self.TestSerializer()
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        self.assertNotEqual(t1, t2)

    def test_encryption(self):
        """Test that token is not encrypted."""
        s = self.TestSerializer()
        t1 = s.create_token(1, dict(recid=1))
        self.assertRaises(
            BadData,
            JSONWebSignatureSerializer('anotherkey').loads,
            t1
        )


class TimedSecretLinkSerializerTestCase(InvenioTestCase):

    """Test case for email link token."""

    def test_create_validate(self):
        """Test token creation."""
        s = TimedSecretLinkSerializer(
            expires_at=datetime.now()+timedelta(days=1))
        t = s.create_token(1234, dict(recid=56789))
        data = s.validate_token(t, expected_data=dict(recid=56789))
        self.assertEqual(data['id'], 1234)
        self.assertEqual(data['data']['recid'], 56789)
        self.assertIsNone(s.validate_token(t, expected_data=dict(recid=1)))

    def test_expired(self):
        """Test token expiry."""
        s = TimedSecretLinkSerializer(
            expires_at=datetime.now()-timedelta(seconds=20))
        t = s.create_token(1, dict(recid=1))
        self.assertIsNone(s.validate_token(t))
        self.assertIsNone(s.validate_token(t, expected_data=dict(recid=1)))
        self.assertRaises(SignatureExpired, s.load_token, t)
        self.assertIsNotNone(s.load_token(t, force=True))

    def test_creation(self):
        """Ensure that no two tokens are identical."""
        s = TimedSecretLinkSerializer(
            expires_at=datetime.now()+timedelta(days=1))
        t1 = s.create_token(98765, dict(recid=4321))
        t2 = s.create_token(98765, dict(recid=4321))
        self.assertNotEqual(t1, t2)


class SecretLinkFactoryTestCase(InvenioTestCase):

    """Test case for factory class."""

    extra_data = dict(recid=1)

    def test_validation(self):
        """Test token validation."""
        t = SecretLinkFactory.create_token(1, self.extra_data)
        self.assertIsNotNone(SecretLinkFactory.validate_token(
            t, expected_data=self.extra_data))

        t = SecretLinkFactory.create_token(
            1, self.extra_data, expires_at=datetime.now()+timedelta(days=1)
        )
        self.assertIsNotNone(SecretLinkFactory.validate_token(
            t, expected_data=self.extra_data))
        self.assertIsNone(SecretLinkFactory.validate_token(
            t, expected_data=dict(recid=2)))

    def test_creation(self):
        """Test token creation."""
        d = datetime.now()+timedelta(days=1)

        t = SecretLinkFactory.create_token(1, self.extra_data)

        self.assertIsNotNone(SecretLinkSerializer().validate_token(
            t, expected_data=self.extra_data))
        self.assertIsNone(TimedSecretLinkSerializer().validate_token(
            t, expected_data=self.extra_data))

        t1 = SecretLinkFactory.create_token(
            1, self.extra_data, expires_at=d
        )
        t2 = SecretLinkFactory.create_token(1, self.extra_data)

        self.assertIsNone(SecretLinkSerializer().validate_token(
            t1, expected_data=self.extra_data))
        self.assertIsNotNone(TimedSecretLinkSerializer().validate_token(
            t1, expected_data=self.extra_data))
        self.assertNotEqual(t1, t2)

    def test_load_token(self):
        """Test token loading."""
        t = SecretLinkFactory.create_token(1, self.extra_data)
        self.assertIsNotNone(SecretLinkFactory.load_token(t))

        t = SecretLinkFactory.create_token(
            1, self.extra_data, expires_at=datetime.now()-timedelta(days=1))
        self.assertRaises(SignatureExpired, SecretLinkFactory.load_token, t)
        self.assertIsNotNone(SecretLinkFactory.load_token(t, force=True))


TEST_SUITE = make_test_suite(
    EmailConfirmationSerializerTestCase,
    SecretLinkSerializerTestCase,
    TimedSecretLinkSerializerTestCase,
    SecretLinkFactoryTestCase
)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
