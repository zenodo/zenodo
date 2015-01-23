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

from flask_email.backends import locmem as mail
from mock import patch

from invenio.base.globals import cfg
from invenio.testsuite import make_test_suite, run_test_suite

from .helpers import BaseTestCase


class ReceiversTestCase(BaseTestCase):

    config = {
        "EMAIL_BACKEND": "flask.ext.email.backends.locmem.Mail"
    }

    render_templates = False

    def tearDown(self):
        if len(mail.outbox) != 0:
            mail.outbox = []
        super(ReceiversTestCase, self).tearDown()

    def test_send_notification(self):
        from zenodo.modules.accessrequests.receivers import \
            _send_notification

        _send_notification(
            "info@invenio-software.org",
            "Test subject",
            "accessrequests/emails/accepted.tpl",
            var1="value1",
        )
        self.assertEqual(len(mail.outbox), 1)

        msg = mail.outbox[0]
        self.assertEqual(msg.to, ["info@invenio-software.org"])
        self.assertEqual(msg.subject, "Test subject")
        self.assertEqual(msg.from_email, cfg["CFG_SITE_SUPPORT_EMAIL"])
        self.assertContext("var1", "value1")
        self.assertTemplateUsed("accessrequests/emails/accepted.tpl")

    @patch('zenodo.modules.accessrequests.receivers.get_record')
    def test_create_secret_link(self, get_record):
        from zenodo.modules.accessrequests.receivers import \
            create_secret_link

        # Patch get_record
        record = dict(
            title="Record Title",
        )
        get_record.return_value = record

        r = self.get_request(confirmed=True)

        create_secret_link(r)

        self.assertEqual(r.link.title, "Record Title")
        self.assertEqual(r.link.description, "")
        self.assertTemplateUsed("accessrequests/link_description.tpl")
        self.assertContext("request", r)
        self.assertContext("record", record)

    @patch('zenodo.modules.accessrequests.receivers.get_record')
    def test_create_secret_link_norecord(self, get_record):
        from zenodo.modules.accessrequests.errors import RecordNotFound
        from zenodo.modules.accessrequests.receivers import \
            create_secret_link

        # Patch get_record
        get_record.return_value = None

        r = self.get_request(confirmed=True)
        self.assertRaises(RecordNotFound, create_secret_link, r)


TEST_SUITE = make_test_suite(ReceiversTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
