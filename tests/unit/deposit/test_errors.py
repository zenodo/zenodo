# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Unit tests for deposit."""

from __future__ import absolute_import, print_function

import json

from flask import Flask

from zenodo.modules.deposit.errors import MarshmallowErrors
from zenodo.modules.deposit.loaders import legacyjson_v1_translator


def m(**kwargs):
    """Make a metadata dictionary."""
    return dict(metadata=kwargs)


def assert_err(data, field):
    """Assert that a certain error is present when loading data."""
    try:
        legacyjson_v1_translator(data)
        raise AssertionError('Did not raise MarshmallowErrors.')
    except MarshmallowErrors as e:
        body = json.loads(e.get_body())

        if field:
            found = False
            for err in body['errors']:
                if field == err['field']:
                    found = True
            if not found:
                raise AssertionError('Field {0} not found.'.format(field))


def test_level1_unknown_key():
    """Test level 1 key errors."""
    assert_err(
        dict(unknownkey='invalid'),
        'unknownkey',
    )


def test_level2_key():
    """Test level 2 key errors."""
    assert_err(
        m(publication_date='invalid'),
        'metadata.publication_date',
    )


def test_level3_list():
    """Test level 3 list key errors."""
    # Min length 1 failure
    assert_err(
        m(creators=[]),
        'metadata.creators',
    )
    # Missing name
    assert_err(
        m(creators=[dict(affiliation='CERN')]),
        'metadata.creators.0.name',
    )

    # Invalid type.
    app = Flask(__name__)
    app.config['DEPOSIT_CONTRIBUTOR_DATACITE2MARC'] = {}
    with app.app_context():
        assert_err(
            m(contributors=[dict(name='a', affiliation='b', type='invalid')]),
            'metadata.contributors.0.type',
        )

    # Unknown key
    assert_err(
        m(creators=[dict(unknownkey='CERN')]),
        'metadata.creators.0.unknownkey',
    )


def test_upload_type():
    """Test upload type."""
    # Invalid type
    assert_err(
        m(upload_type='invalid'),
        'metadata.upload_type',
    )
    # Invalid subtype
    assert_err(
        m(upload_type='publication', subtype='invalid'),
        'metadata.publication_type',
    )
    assert_err(
        m(upload_type='image', subtype='invalid'),
        'metadata.image_type',
    )


def test_related_identifiers():
    """Test related identifiers."""
    cases = [
        # No identifier
        dict(identifier='', relation='cites'),
        # Non-detectable identifier
        dict(identifier='abc', relation='cites'),
        # Invalid identifier for scheme.
        dict(identifier='10.1234/foo', scheme='orcid', relation='cites'),
    ]
    for c in cases:
        assert_err(
            m(related_identifiers=[c]),
            'metadata.related_identifiers.0.identifier',
        )

    # Invalid relation
    assert_err(
        m(related_identifiers=[dict(relation='invalid')]),
        'metadata.related_identifiers.0.relation',
    )
