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

from flask import url_for
from helpers import publish_and_expunge
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
        license_record, minimal_deposit, communities, deposit_url,
        ):
    """Test deposit with custom field publishing."""
    auth_headers = json_auth_headers

    # Test wrong community
    minimal_deposit['metadata']['custom'] = {
        "not-custom-metadata-community": {
            "family": {"value": "Felidae",
                       "uri": "https://en.wikipedia.org/wiki/Felidae"},
            }
    }
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)
    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'The community: not-custom-metadata-community is'
                   ' not supporting custom metadata'
            }]

    # Test wrong scheme
    minimal_deposit['metadata']['custom'] = {
        "custom-metadata-community": {
            "non-existent-scheme": {
                "value": "Felidae",
                "uri": "https://en.wikipedia.org/wiki/Felidae"
                }
            }
    }
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)
    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'The community custom-metadata-community is not supporting'
                   ' non-existent-scheme as a metadata scheme'
            }]

    # Test wrong value
    minimal_deposit['metadata']['custom'] = {
        "custom-metadata-community": {
            "family": {"value": 12131,
                       "uri": "https://en.wikipedia.org/wiki/Felidae"}
            }
    }
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)
    assert response.json['errors'] == [{
        'field': 'metadata.custom.value',
        'message': 'Not a valid string.'
            }]

    # Test that the used community for custom metadata is in the record
    minimal_deposit['metadata']['custom'] = {
        "custom-metadata-community": {
            "family": {"value": "Felidae",
                       "uri": "https://en.wikipedia.org/wiki/Felidae"},
            "behavior": {"value": "Plays with yarn, sleeps in cardboard box."}
            }
    }
    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    assert response.json['errors'] == [{
        'field': 'metadata.custom',
        'message': 'You have included custom metadata for communities'
                   ' this record does not belong to.'
            }]

    # Add the missing community creating a valid record with custom metadata
    minimal_deposit['metadata']['communities'] = \
        [{'identifier': 'custom-metadata-community'}]

    response = api_client.post(
        deposit_url, json=minimal_deposit, headers=auth_headers)

    links = response.json['links']
    expected_custom_data = {
        "custom-metadata-community": {
            "family": {
                "scheme": "http://rs.tdwg.org/dwc/terms/family",
                "uri": "https://en.wikipedia.org/wiki/Felidae",
                "value": "Felidae"
            },
            "behavior": {
                'scheme': 'http://rs.tdwg.org/dwc/iri/behavior',
                "value": "Plays with yarn, sleeps in cardboard box."
            }
        }
    }
    assert response.json['metadata']['custom'] == expected_custom_data

    response = api_client.put(
            links['bucket']+'/test',
            data='foo file',
            headers=auth_headers,
        )
    assert response.status_code == 200

    # Publish the record
    response = api_client.post(links['publish'], headers=auth_headers)

    # Get published record
    response = api_client.get(response.json['links']['record'])
    assert response.json['metadata']['custom'] == expected_custom_data
