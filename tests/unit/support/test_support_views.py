# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Unit tests support utils."""

from __future__ import absolute_import, print_function

from flask import url_for
from helpers import login_user_via_session, recaptcha_enabled
from six import BytesIO, b
from werkzeug import MultiDict


def test_send_support_email(app, db, es, users):
    """Test mail sending."""
    with app.extensions['mail'].record_messages() as outbox:
        with app.test_client() as client:
            res = client.get(url_for('zenodo_support.support'))
            assert res.status_code == 200

            with recaptcha_enabled(app):
                res = client.get(
                    url_for('zenodo_support.support')
                )
                assert b('recaptcha') in res.data
                assert res.status_code == 200

            res = client.post(
                url_for('zenodo_support.support'),
                data=dict()
            )
            assert res.status_code == 200
            assert b('field-name has-error') in res.data
            assert b('field-email has-error') in res.data
            assert b('field-subject has-error') in res.data
            assert b('field-description has-error') in res.data
            assert b('field-attachments has-error') not in res.data

            form = MultiDict(dict(
                name='Aman',
                email='abcxyz@example.com',
                subject='hello',
                issue_category='tech-support',
                description='Please help us! Troubleshoot our problem.'
            ))

            res = client.post(
                url_for('zenodo_support.support'),
                data=form
            )
            assert b('has-error') not in res.data
            assert len(outbox) == 2
            sent_msg = outbox[0]
            assert sent_msg.sender == 'Aman <abcxyz@example.com>'
            assert sent_msg.subject == '[tech-support]: hello'
            assert sent_msg.reply_to == 'abcxyz@example.com'
            assert 'Aman <abcxyz@example.com>' in sent_msg.body

            sent_msg = outbox[1]
            assert sent_msg.sender == 'Zenodo <info@zenodo.org>'
            assert sent_msg.subject == 'Zenodo Support'
            assert sent_msg.body == (
                'Thank you for contacting Zenodo support.'
                '\n\nWe have received your message, and we will do our best '
                'to get back to you as soon as possible.\nThis is an '
                'automated confirmation of your request, please do not reply '
                'to this email.\n\nZenodo Support\n'
                'https://zenodo.org\n'
            )

            form = MultiDict(dict(
                name='Foo',
                email='example@mail.com',
                subject='Bar',
                issue_category='tech-support',
                description='Please help us! Troubleshoot our problem.'
            ))
            test_file = BytesIO(b('My other file contents'))
            test_file2 = BytesIO(b('Another My other file contents'))
            form.add('attachments', (test_file, 'file2.txt'))
            form.add('attachments', (test_file2, 'test3.txt'))
            res = client.post(
                url_for('zenodo_support.support'),
                data=form,
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert len(outbox) == 4
            sent_msg = outbox[2]
            file1 = sent_msg.attachments[0]
            assert file1.filename == 'file2.txt'
            assert file1.data == b('My other file contents')
            file2 = sent_msg.attachments[1]
            assert file2.filename == 'test3.txt'
            assert file2.data == b('Another My other file contents')

            login_user_via_session(client, email=users[1]['email'])

            with recaptcha_enabled(app):
                res = client.get(
                    url_for('zenodo_support.support')
                )
                assert b('test@zenodo.org') in res.data
                assert b('recaptcha') not in res.data

            form = MultiDict(dict(
                name='Foo',
                subject='Bar',
                issue_category='tech-support',
                description='Please help us! Troubleshoot our problem.'
            ))
            res = client.post(
                url_for('zenodo_support.support'),
                data=form
            )
            assert len(outbox) == 6
            sent_msg = outbox[4]
            assert 'From: Foo <test@zenodo.org> (2)' in sent_msg.body

            test_file = BytesIO(b('My file contents'))
            form.add('attachments', (test_file, 'file1.txt'))
            res = client.post(
                url_for('zenodo_support.support'),
                data=form,
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert len(outbox) == 8
            sent_msg = outbox[6]
            file1 = sent_msg.attachments[0]
            assert file1.filename == 'file1.txt'
            assert file1.data == b('My file contents')

            form = MultiDict(dict(
                name='Foo',
                subject='Bar',
                issue_category='tech-support',
                description='Please help us! Troubleshoot our problem.'
            ))
            test_file = BytesIO(b('My other file contents'))
            test_file2 = BytesIO(b('Another My other file contents'))
            form.add('attachments', (test_file, 'file2.txt'))
            form.add('attachments', (test_file2, 'test3.txt'))
            res = client.post(
                url_for('zenodo_support.support'),
                data=form,
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert len(outbox) == 10
            sent_msg = outbox[8]
            file1 = sent_msg.attachments[0]
            assert file1.filename == 'file2.txt'
            assert file1.data == b('My other file contents')
            file2 = sent_msg.attachments[1]
            assert file2.filename == 'test3.txt'
            assert file2.data == b('Another My other file contents')
