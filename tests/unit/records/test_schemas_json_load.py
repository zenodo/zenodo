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

"""Unit tests Zenodo JSON deserializer."""

from __future__ import absolute_import, print_function

from datetime import datetime

import idutils
import pytest

from zenodo.modules.records.serializers.schemas.json import MetadataSchemaV1


@pytest.mark.parametrize('input_val, ctx', [
    ('10.1234/foo.bar', dict()),
    ('http://dx.doi.org/10.1234/foo.bar', dict()),
    ('https://doi.org/10.1234/foo.bar', dict()),
    (' doi:10.1234/foo.bar ', dict()),
    (' 10.1234/foo.bar ', dict()),
    ('10.5281/allow', dict(
        allowed_dois=['10.5281/allow'],
        managed_prefixes=['10.5281']
    )),
    ('10.5281/required', dict(
        required_doi='10.5281/required',
        allowed_dois=['10.5281/allow'],
        managed_prefixes=['10.5281'])),
])
def test_valid_doi(input_val, ctx):
    """Test DOI."""
    data, errors = MetadataSchemaV1(
        partial=['doi'], context=ctx).load(dict(doi=input_val))
    assert data['doi'] == idutils.normalize_doi(input_val.strip())


@pytest.mark.parametrize(('input_val', 'ctx'), [
    ('10.5072/test.prefix', dict()),
    ('not a doi', dict()),
    ('10.5281/banned_prefix', dict(managed_prefixes=['10.5281'])),
    ('10.5281/allow', dict(
        required_doi='10.5281/required',
        allowed_dois=['10.5281/allow'],
        managed_prefixes=['10.5281'])),
    ('10.5281/invalid', dict(
        allowed_dois=['10.5281/allow'],
        managed_prefixes=['10.5281'])),
    ('10.5281/invalid_prefix', dict(banned_prefixes=['10.5281', '10.5072'])),
    ('10.5072/invalid_prefix', dict(banned_prefixes=['10.5281', '10.5072'])),
])
def test_invalid_doi(input_val, ctx):
    """Test DOI."""
    data, errors = MetadataSchemaV1(
        partial=['doi'], context=ctx).load(dict(doi=input_val))
    assert 'doi' in errors
    assert 'doi' not in data


@pytest.mark.parametrize(('val', 'expected'), [
    (dict(type='publication', subtype='preprint'), None),
    (dict(type='image', subtype='photo'), None),
    (dict(type='dataset'), None),
    (dict(type='dataset', title='Dataset'), dict(type='dataset')),
])
def test_valid_resource_type(val, expected):
    """Test resource type."""
    data, errors = MetadataSchemaV1(partial=['resource_type']).load(
        dict(resource_type=val))
    assert data['resource_type'] == val if expected is None else expected


@pytest.mark.parametrize('val', [
    dict(type='image', subtype='preprint'),
    dict(subtype='photo'),
    dict(type='invalid'),
    dict(title='Dataset'),
    dict(),
])
def test_invalid_resource_type(val):
    """Test resource type."""
    data, errors = MetadataSchemaV1(partial=['resource_type']).load(
        dict(resource_type=val))
    assert 'resource_type' in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ('2016-01-02', '2016-01-02'),
    (' 2016-01-02 ', '2016-01-02'),
    ('0001-01-01', '0001-01-01'),
    (None, datetime.utcnow().date().isoformat()),
    ('2016', datetime.utcnow().date().isoformat()),
])
def test_valid_publication_date(val, expected):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=['publication_date']).load(
        dict(publication_date=val) if val is not None else dict())
    assert data['publication_date'] == val if expected is None else expected


def test_language():
    """Test resource type."""
    msv1 = MetadataSchemaV1(partial=['language'])
    data, errors = msv1.load(dict(language='eng'))
    assert data['language'] == 'eng'
    assert 'language' not in errors
    data, errors = msv1.load(dict(language='English'))
    assert 'language' in errors
    data, errors = msv1.load(dict())
    assert 'language' not in errors


@pytest.mark.parametrize('val', [
    '2016-02-32',
    ' invalid',
])
def test_invalid_publication_date(val):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=['publication_date']).load(
        dict(publication_date=val))
    assert 'publication_date' in errors
    assert 'publication_date' not in data


@pytest.mark.parametrize(('val', 'expected'), [
    ('Test', 'Test',),
    (' Test ', 'Test'),
    ('', None),
    ('  ', None),
])
def test_title(val, expected):
    """Test title."""
    data, errors = MetadataSchemaV1(partial=['title']).load(
        dict(title=val))
    if expected is not None:
        assert data['title'] == expected
    else:
        assert 'title' in errors
        assert 'title' not in data


def test_dates():
    """Test dates."""
    schema = MetadataSchemaV1(partial=['dates'])

    data, errors = schema.load({'dates': None})
    assert 'not be null' in errors['dates'][0]
    data, errors = schema.load({'dates': []})
    assert 'Shorter than minimum' in errors['dates'][0]
    data, errors = schema.load({'dates': [{}]})
    assert 'required field' in errors['dates'][0]['type'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid'}]})
    assert 'at least one date' in errors['dates'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid', 'start': None}]})
    assert 'not be null' in errors['dates'][0]['start'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid', 'start': ''}]})
    assert 'Not a valid date' in errors['dates'][0]['start'][0]

    # "start" date after "end"
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-02-01', 'end': '2019-01-01'}]})
    assert 'must be before "end"' in errors['dates'][0]

    # Single date value (i.e. start == end)
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-01-01', 'end': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid', 'start': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid', 'end': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-01-01', 'end': '2019-01-31',
                    'description': 'Some description'}]})
    assert 'dates' not in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ([{'lat': '2.35', 'lon': '1.534', 'place': 'my place'}],
     {'lat': 2.35, 'lon': 1.534, 'place': 'my place'},),
    ([{'lat': 2.35, 'lon': 1.534, 'place': 'my place'}],
     {'lat': 2.35, 'lon': 1.534, 'place': 'my place'}),
    ({'lat': 2.35, 'place': 'my place'}, None),
    ({'lon': 1.534, 'place': 'my place'}, None),
    ({'lat': 2.35, 'lon': 1.534}, None),
    ({'lat': None, 'lon': 1.534, 'place': 'my place'}, None),
    ({'lat': 2.35, 'lon': 91, 'place': 'my place'}, None),
    ({'lat': -91, 'lon': 1.534, 'place': 'my place'}, None),
    ([{'lat': -90, 'lon': 90, 'place': 'my place'}],
     {'lat': -90, 'lon': 90, 'place': 'my place'}),
])
def test_geographical_metadata(val, expected):
    """Test geographical metadata."""
    data, errors = MetadataSchemaV1(partial=['locations']).load(
        dict(locations=val))
    if expected is not None:
        assert data['locations'][0] == expected
    else:
        assert 'locations' in errors
        assert 'locations' not in data
