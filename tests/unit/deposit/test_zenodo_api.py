# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import hashlib
import json
from time import sleep

from flask import url_for
from six import BytesIO

from invenio_deposit.api import Deposit


def make_pdf_fixture(filename, text=None):
    """Generate a PDF fixture."""
    content = text or b''
    digest = 'md5:{0}'.format(hashlib.md5(content).hexdigest())
    return (BytesIO(content), filename)


def test_simple_rest_flow(app, db, es, location, users, write_token):
    """Test simple flow using REST API."""
    test_data = dict(
        metadata=dict(
            upload_type='presentation',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
                dict(name='Smith, Jane', affiliation='Atlantis')
            ],
            description='Test Description',
            publication_date='2013-05-08',
        )
    )
    auth = [
        ('Authorization', 'Bearer {0}'.format(write_token)),
    ]
    headers = [('Content-Type', 'application/json'),
               ('Accept', 'application/json')]
    auth_headers = headers + auth
    deposit_url = '/api/deposits/'

    with app.test_client() as client:
        # try create deposit as anonymous user (failing)
        response = client.post(deposit_url, data=json.dumps(test_data),
                               headers=headers)
        assert response.status_code == 401

        # Create deposition
        response = client.post(deposit_url, data=json.dumps(test_data),
                               headers=auth_headers)
        assert response.status_code == 201

        data = json.loads(response.data.decode('utf-8'))
        deposit = data['metadata']
        links = data['links']

        sleep(5)

        # Get deposition
        response = client.get(links['self'], headers=auth)
        assert response.status_code == 200

        # Upload 3 files
        for i in range(3):
            response = client.post(
                links['files'],
                data={
                    'file': make_pdf_fixture('test{0}.pdf'.format(i)),
                    'name': 'test-{0}.pdf'.format(i),
                },
                headers=auth,
            )
            assert response.status_code == 201, i

        # Publish deposition
        response = client.post(links['publish'], headers=auth_headers)
        assert response.status_code == 202

        #
        # Test for workflow status
        #
        # TODO check that record exists

        # Second request will return forbidden since it's already published
        response = client.post(links['publish'])
        assert response.status_code == 403  # FIXME should be 400

        # Not allowed to edit drafts
        response = client.put(links['self'], data=json.dumps(test_data),
                              headers=auth_headers)
        assert response.status_code == 403

        # Not allowed to delete
        response = client.delete(links['self'], data=json.dumps(test_data),
                                 headers=auth)
        assert response.status_code == 403

        # Not allowed to sort files
        response = client.get(links['files'], headers=auth_headers)
        assert response.status_code == 200

        files_list = map(lambda x: {'id': x['id']}, response.json)
        files_list.reverse()
        response = client.put(links['files'], data=json.dumps(files_list),
                              headers=auth)
        assert response.status_code == 403

        # Not allowed to add files
        i = 5
        response = client.post(
            links['files'],
            data={
                'file': make_pdf_fixture('test{0}.pdf'.format(i)),
                'name': 'test-{0}.pdf'.format(i),
            },
            headers=auth,
        )
        assert response.status_code == 403

        # Not allowed to delete file
        assert links['files'][-1] == '/'
        response = client.delete(links['files'] + files_list[0]['id'],
                                 headers=auth)
        assert response.status_code == 403

        # Not allowed to rename file
        response = client.put(
            links['files'] + files_list[0]['id'],
            data=json.dumps(dict(filename='another_test.pdf')),
            headers=auth_headers,
        )
        assert response.status_code == 403

        # check submitted record
