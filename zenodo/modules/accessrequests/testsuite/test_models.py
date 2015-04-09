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

"""Model tests."""

from __future__ import absolute_import

from datetime import datetime, timedelta

from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import BaseTestCase


class AccessRequestTestCase(BaseTestCase):

    """Test of access request model."""

    def test_create_nouser(self):
        """Test access request creation without user."""
        from zenodo.modules.accessrequests.models import AccessRequest, \
            RequestStatus
        from zenodo.modules.accessrequests.signals import \
            request_created, request_confirmed

        with request_created.connected_to(self.get_receiver('created')):
            with request_confirmed.connected_to(
                 self.get_receiver('confirmed')):

                r = AccessRequest.create(
                    recid=1,
                    receiver=self.receiver,
                    sender_full_name="John Smith",
                    sender_email="info@invenio-software.org",
                    justification="Bla bla bla",
                )

                self.assertEqual(r.status, RequestStatus.EMAIL_VALIDATION)
                self.assertIsNone(r.sender_user_id)
                self.assertIsNotNone(r.created)
                self.assertIsNotNone(r.modified)
                self.assertEqual(r.message, u'')

                self.assertIsNotNone(self.called['created'])
                self.assertIsNone(self.called['confirmed'])

    def test_create_withuser(self):
        """Test access request creation with user."""
        from zenodo.modules.accessrequests.models import AccessRequest, \
            RequestStatus
        from zenodo.modules.accessrequests.signals import \
            request_created, request_confirmed

        with request_created.connected_to(self.get_receiver('created')):
            with request_confirmed.connected_to(
                 self.get_receiver('confirmed')):
                r = AccessRequest.create(
                    recid=1,
                    receiver=self.receiver,
                    sender_full_name="Another Name",
                    sender_email="anotheremail@example.org",
                    sender=self.sender,
                    justification="Bla bla bla",
                )

                self.assertEqual(r.status, RequestStatus.PENDING)
                self.assertEqual(r.sender_user_id, self.sender.get_id())
                self.assertIsNotNone(r.created)
                self.assertIsNotNone(r.modified)
                self.assertEqual(r.message, u'')
                self.assertEqual(r.sender_full_name, u'Another Name')
                self.assertEqual(r.sender_email, u'anotheremail@example.org')

                self.assertIsNone(self.called['created'])
                self.assertIsNotNone(self.called['confirmed'])

    def test_accept(self):
        """Test accept signal and state."""
        from zenodo.modules.accessrequests.errors import \
            InvalidRequestStateError
        from zenodo.modules.accessrequests.models import RequestStatus
        from zenodo.modules.accessrequests.signals import \
            request_accepted

        with request_accepted.connected_to(self.get_receiver('accepted')):

            # Invalid operation when email not confirmed
            r = self.get_request(confirmed=False)
            self.assertRaises(InvalidRequestStateError, r.accept)
            self.assertIsNone(self.called['accepted'])

            # Test signal and state
            r = self.get_request(confirmed=True)
            r.accept()
            self.assertEqual(r.status, RequestStatus.ACCEPTED)
            self.assertIsNotNone(self.called['accepted'])
            self.assertEqual(
                r,
                self.called['accepted']['args'][0]
            )

            # Invalid operation for accepted request
            self.assertRaises(InvalidRequestStateError, r.confirm_email)

    def test_reject(self):
        """Test reject signal and state."""
        from zenodo.modules.accessrequests.errors import \
            InvalidRequestStateError
        from zenodo.modules.accessrequests.models import RequestStatus
        from zenodo.modules.accessrequests.signals import \
            request_rejected

        with request_rejected.connected_to(self.get_receiver('rejected')):

            r = self.get_request(confirmed=False)
            self.assertRaises(InvalidRequestStateError, r.reject)
            self.assertIsNone(self.called['rejected'])

            r = self.get_request(confirmed=True)
            r.reject()
            self.assertEqual(r.status, RequestStatus.REJECTED)
            self.assertEqual(
                r,
                self.called['rejected']['args'][0]
            )

            self.assertRaises(InvalidRequestStateError, r.confirm_email)

    def test_confirm_email(self):
        """Test confirm email signal and state."""
        from zenodo.modules.accessrequests.models import RequestStatus

        from zenodo.modules.accessrequests.signals import \
            request_confirmed

        with request_confirmed.connected_to(self.get_receiver('confirmed')):
            r = self.get_request(confirmed=False)
            r.confirm_email()
            self.assertEqual(r.status, RequestStatus.PENDING)
            self.assertEqual(
                r,
                self.called['confirmed']['args'][0]
            )

    def test_query_by_receiver(self):
        """Test query by receiver."""
        from zenodo.modules.accessrequests.models import AccessRequest
        self.assertEqual(
            AccessRequest.query_by_receiver(self.receiver).count(),
            0)
        self.assertEqual(
            AccessRequest.query_by_receiver(self.sender).count(),
            0)

        # Create an accesrequest
        r = self.get_request(confirmed=False)

        self.assertEqual(
            AccessRequest.query_by_receiver(self.receiver).count(),
            1)
        self.assertEqual(
            AccessRequest.query_by_receiver(self.sender).count(),
            0)

        self.assertIsNotNone(AccessRequest.get_by_receiver(
            r.id, self.receiver))
        self.assertIsNone(AccessRequest.get_by_receiver(
            r.id, self.sender))

    def test_create_secret_link(self):
        """Test creation of secret link via token."""
        r = self.get_request(confirmed=False)
        l = r.create_secret_link(
            "My link", "Link description",
            expires_at=datetime.now()+timedelta(days=1)
        )
        assert r.link == l
        self.assertEqual(l.title, "My link")
        self.assertEqual(l.description, "Link description")
        self.assertEqual(l.extra_data, dict(recid=1))
        self.assertEqual(l.owner, self.receiver)


class SecretLinkTestCase(BaseTestCase):

    """Test of secret link model."""

    def test_creation(self):
        """Test link creation."""
        from zenodo.modules.accessrequests.models import SecretLink

        from zenodo.modules.accessrequests.signals import \
            link_created

        with link_created.connected_to(self.get_receiver('created')):
            l = SecretLink.create("Test title", self.receiver, dict(recid=1),
                                  description="Test description")

            self.assertEqual(l.title, "Test title")
            self.assertEqual(l.description, "Test description")
            self.assertIsNone(l.expires_at)
            self.assertNotEqual(l.token, "")
            self.assertIsNotNone(self.called['created'])

            assert SecretLink.validate_token(l.token, dict(recid=1),)
            assert not SecretLink.validate_token(l.token, dict(recid=2))

    def test_revoked(self):
        """Test link revocation."""
        from zenodo.modules.accessrequests.models import SecretLink

        from zenodo.modules.accessrequests.signals import \
            link_revoked

        with link_revoked.connected_to(self.get_receiver('revoked')):
            l = SecretLink.create(
                "Test title", self.receiver, dict(recid=123456),
                description="Test description"
            )
            assert not l.is_revoked()
            assert l.is_valid()
            l.revoke()
            assert l.is_revoked()
            assert not l.is_valid()

            self.assertIsNotNone(self.called['revoked'])

            self.assertFalse(l.revoke())

    def test_expired(self):
        """Test link expiry date."""
        from zenodo.modules.accessrequests.models import SecretLink

        l = SecretLink.create(
            "Test title", self.receiver, dict(recid=123456),
            description="Test description",
            expires_at=datetime.now()-timedelta(days=1))
        assert l.is_expired()
        assert not l.is_valid()

        l = SecretLink.create(
            "Test title", self.receiver, dict(recid=123456),
            description="Test description",
            expires_at=datetime.now()+timedelta(days=1))
        assert not l.is_expired()
        assert l.is_valid()

    def test_query_by_owner(self):
        """Test query by owner."""
        from zenodo.modules.accessrequests.models import SecretLink

        self.assertEqual(
            SecretLink.query_by_owner(self.receiver).count(),
            0)
        self.assertEqual(
            SecretLink.query_by_owner(self.sender).count(),
            0)

        SecretLink.create("Testing", self.receiver, dict(recid=1))

        self.assertEqual(
            SecretLink.query_by_owner(self.receiver).count(),
            1)
        self.assertEqual(
            SecretLink.query_by_owner(self.sender).count(),
            0)

    def test_get_absolute_url(self):
        """Test absolute url."""
        from zenodo.modules.accessrequests.models import SecretLink

        l = SecretLink.create("Testing", self.receiver, dict(recid=1))
        url = l.get_absolute_url('record.metadata')
        assert "/record/1?" in url
        assert "token={0}".format(l.token) in url


TEST_SUITE = make_test_suite(AccessRequestTestCase, SecretLinkTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
