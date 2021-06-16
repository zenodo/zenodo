# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Test Zenodo Deposit API."""

from __future__ import absolute_import, print_function

import json
from copy import deepcopy

import pytest
from flask import url_for
from helpers import login_user_via_session, publish_and_expunge
from invenio_pidrelations.contrib.versioning import PIDVersioning

from zenodo.modules.records.resolvers import record_resolver


def test_basic_deposit_edit(app, db, communities, deposit, deposit_file):
    """Test simple deposit publishing."""
    deposit = publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    initial_oai = deepcopy(record['_oai'])

    # Create some potential corruptions to protected fields
    deposit = deposit.edit()
    deposit['_files'][0]['bucket'] = record['_buckets']['deposit']
    deposit['_oai'] = {}
    deposit = publish_and_expunge(db, deposit)
    pid, record = deposit.fetch_published()
    assert record['_oai'] == initial_oai
    assert record['_files'][0]['bucket'] == record['_buckets']['record']


def test_deposit_versioning_draft_child_unlinking_bug(
        app, db, communities, deposit, deposit_file):
    """
    Bug with draft_child_deposit unlinking.

    Bug where a draft_child_deposit was unlinked from a new version draft,
    when another version of a record was edited and published.
    """
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit.fetch_published()
    recid_v1_value = recid_v1.pid_value

    # Initiate a new version draft
    deposit_v1.newversion()
    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    pv = PIDVersioning(child=recid_v1)
    assert pv.draft_child_deposit
    assert pv.draft_child

    deposit_v1.edit()
    deposit_v1 = deposit_v1.edit()
    deposit_v1 = publish_and_expunge(db, deposit_v1)

    recid_v1, record_v1 = record_resolver.resolve(recid_v1_value)
    pv = PIDVersioning(child=recid_v1)
    # Make sure the draft child deposit was not unliked due to publishing of
    # the edited draft
    assert pv.draft_child_deposit
    assert pv.draft_child


def test_deposit_with_custom_field(
    json_auth_headers, api, api_client, db, es, locations, users,
        license_record, minimal_deposit, deposit_url,
        ):
    """Test deposit with custom field publishing."""
    auth_headers = json_auth_headers

    # Test wrong term
    minimal_deposit['metadata']['custom'] = {'dwc:foobar': 'Felidae'}
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)
    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message':
        'Zenodo does not support "dwc:foobar" as a custom metadata term.'}]

    # Test wrong value
    minimal_deposit['metadata']['custom'] = {
        'dwc:family': [12131]
    }
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)
    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'Invalid type for term "dwc:family", should be "keyword".'}]

    # Test data not provided in an array
    minimal_deposit['metadata']['custom'] = {
        'dwc:family': 'Fox'
    }

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'Term "dwc:family" should be of type array.'}]

    # Test null data
    minimal_deposit['metadata']['custom'] = {
        'dwc:genus': None,
        'dwc:family': ['Felidae'],
    }

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'Term "dwc:genus" should be of type array.'}]

    # Test null data
    minimal_deposit['metadata']['custom'] = {
        'dwc:family': [],
        'dwc:behavior': ['Plays with yarn, sleeps in cardboard box.'],
    }

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'No values were provided for term "dwc:family".'}]

    # Test null data
    minimal_deposit['metadata']['custom'] = {
        'dwc:family': ['Felidae'],
        'dwc:behavior': ['foobar', None],
    }

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'Invalid type for term "dwc:behavior", should be "text".'}]

    # Test null data
    minimal_deposit['metadata']['custom'] = {
        'dwc:family': ['Felidae'],
        'dwc:behavior': [None],
    }

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'Invalid type for term "dwc:behavior", should be "text".'}]

    expected_custom_data = {
        'dwc:family': ['Felidae'],
        'dwc:genus': ['Nighty', 'Reddish'],
        'dwc:behavior': ['Plays with yarn, sleeps in cardboard box.'],
    }

    minimal_deposit['metadata']['custom'] = expected_custom_data

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['metadata']['custom'] == expected_custom_data
    links = response.json['links']

    response = api_client.put(
            links['bucket'] + '/test',
            data='foo file',
            headers=auth_headers,
        )
    assert response.status_code == 200

    # Publish the record
    response = api_client.post(links['publish'], headers=auth_headers)

    # Get published record
    response = api_client.get(response.json['links']['record'])
    assert response.json['metadata']['custom'] == expected_custom_data


@pytest.mark.parametrize('user_info,status', [
    # anonymous user
    (None, 401),
    # validated user
    (dict(email='info@zenodo.org', password='tester'), 201),
    # non validated user
    (dict(email='nonvalidated@zenodo.org', password='tester'), 403),
    # validated but with blacklisted domain
    (dict(email='validated@evildomain.org', password='tester'), 403),
    # validated for a long time with blacklisted domain
    (dict(email='longvalidated@evildomain.org', password='tester'), 403),
    # non validated with blacklisted domain and external ids
    (dict(email='external@evildomain.org', password='tester'), 403),
])
def test_deposit_create_permissions(
        api, api_client, db, es, users, minimal_deposit, license_record,
        deposit_url, locations, user_info, status):
    """Test deposit with custom field publishing."""
    if user_info:
        login_user_via_session(api_client, email=user_info['email'])
    # Test wrong term
    response = api_client.post(
        deposit_url, json=minimal_deposit)
    assert response.status_code == status
