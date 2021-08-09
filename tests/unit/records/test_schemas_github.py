# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2021 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo GitHub schemas tests."""

from __future__ import absolute_import, print_function

from datetime import datetime

import idutils
import pytest
from invenio_records.api import Record
from jsonschema.exceptions import ValidationError

from zenodo.modules.github.schemas import CitationMetadataSchema


def test_github_schema():
    """Tests Github Citation metadata schema."""
    test_data = {
        "cff-version": "1.1.0",
        "message": "If you use this software, please cite it as below.",
        "authors":
            [{
                "family-names": "Joe",
                "given-names": "Johnson",
                "orcid": "https://orcid.org/0000-0000-0000-0000"
            }],
        "title": "My Research Software",
        "version": "2.0.10",
        "date-released": "2017-12-18",
        "references":
        [{
            "type": "book",
            "identifiers": [
                {
                    "type": "swh",
                    "value":
                    "swh:1:rel:99f6850374dc6597af01bd0ee1d3fc0699301b9f"
                },
                {
                    "type": "other",
                    "value": "my-custom-identifier-1234dasd"
                }
            ]
        }],
        "identifiers":
        [
            {
                "type": "swh",
                "value":
                "swh:1:rel:99f6850374dc6597af01bd0ee1d3fc0699301b81"
            },
            {
                "type": "other",
                "value": "my-custom-identifier-1234dasd"
            }
                ]
    }
    expected = {
        'alternate_identifiers': [
            {'scheme': 'swh',
             'identifier': 'swh:1:rel:99f6850374dc6597af01bd0ee1d3fc0699301b81',
             'resource_type': 'other'}
        ],
        'title': 'My Research Software',
        'notes': 'If you use this software, please cite it as below.',
        'version': '2.0.10',
        'publication_date': '2017-12-18',
        'creators': [{'name': 'Joe, Johnson'}],
        'related_identifiers': [
            {'scheme': 'swh',
             'identifier': 'swh:1:rel:99f6850374dc6597af01bd0ee1d3fc0699301b9f',
             'relation': 'references',
             'resource_type': 'publication-book'}
        ]
    }
    schema = CitationMetadataSchema(context={'replace_refs': True})

    result = schema.load(test_data)
    assert result.data == expected
