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

from __future__ import absolute_import

from invenio.testsuite import InvenioTestCase
from invenio.ext.sqlalchemy import db


class BaseTestCase(InvenioTestCase):
    def setUp(self):
        from zenodo.modules.accessrequests.models import AccessRequest, \
            SecretLink
        from invenio.modules.accounts.models import User

        AccessRequest.query.delete()
        SecretLink.query.delete()
        User.query.filter_by(nickname='sender').delete()
        User.query.filter_by(nickname='receiver').delete()

        self.sender = User(
            nickname="sender",
            family_name="sender",
            given_names="a",
            password="sender",
            note="1",

        )
        self.receiver = User(
            nickname="receiver",
            family_name="receiver",
            given_names="a",
            password="receiver",
            note="1"
        )

        db.session.add(self.sender)
        db.session.add(self.receiver)
        db.session.commit()

        self.called = dict()

    def tearDown(self):
        db.session.expunge_all()

    def get_receiver(self, name):
        """Create a signal receiver."""
        self.called[name] = None

        def _receiver(*args, **kwargs):
            self.called[name] = dict(args=args, kwargs=kwargs)

        return _receiver

    def get_request(self, confirmed=False):
        from zenodo.modules.accessrequests.models import AccessRequest

        return AccessRequest.create(
            recid=1,
            receiver=self.receiver,
            sender_full_name="Another Name",
            sender_email="anotheremail@example.org",
            sender=self.sender if confirmed else None,
            justification="Bla bla bla",
        )
