# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Test Zenodo records utils."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.utils import build_record_custom_fields, \
    is_valid_openaire_type


def test_openaire_type_validation(app):
    """Test validation of OpenAIRE subtypes."""
    assert is_valid_openaire_type({}, [])
    assert is_valid_openaire_type({'type': 'dataset'}, ['c1', 'b2'])
    # valid case
    assert is_valid_openaire_type(
        {'openaire_subtype': 'foo:t4', 'type': 'other'}, ['c1'])
    # another valid case
    assert is_valid_openaire_type(
        {'openaire_subtype': 'bar:t3', 'type': 'software'}, ['c3'])
    # valid case (mixed communities, but subtype from other/foo)
    assert is_valid_openaire_type(
        {'openaire_subtype': 'foo:t4', 'type': 'other'}, ['c1', 'c3'])
    # valid case (mixed communities, but subtype from software/bar)
    assert is_valid_openaire_type(
        {'openaire_subtype': 'bar:t3', 'type': 'software'}, ['c1', 'c3'])
    # invalid OA subtype
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'xxx', 'type': 'other'}, ['c1'])
    # community missing
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'foo:oth1', 'type': 'other'}, [])
    # wrong community
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'foo:oth1', 'type': 'other'}, ['c3'])
    # wrong general type (software has a definition)
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'foo:t4', 'type': 'software'}, ['c1'])
    # wrong general type (dataset has no definition)
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'foo:t4', 'type': 'dataset'}, ['c1'])
    # non-existing prefix
    assert not is_valid_openaire_type(
        {'openaire_subtype': 'xxx:t1', 'type': 'software'}, ['c1'])


def test_build_record_custom_fields(app, full_record, custom_metadata):
    """Test building of the records' custom fields."""
    full_record['custom'] = custom_metadata
    expected = dict(
        custom_keywords={
            ('dwc:family', ('Felidae',)),
            ('dwc:genus', ('Felis',)),
        },
        custom_text={
            ('dwc:behavior', ('Plays with yarn, sleeps in cardboard box.',)),
        },
        custom_relationships={
            (
                'obo:RO_0002453',
                ('Cat', 'Felis catus'),
                ('Ctenocephalides felis', 'Cat flea'),
            )
        }
    )

    result = build_record_custom_fields(full_record)
    assert expected == {
        'custom_keywords': {
            (v['key'], tuple(v['value'])) for v in result['custom_keywords']},
        'custom_text': {
            (v['key'], tuple(v['value'])) for v in result['custom_text']},
        'custom_relationships': {
            (v['key'], tuple(v['subject']), tuple(v['object']))
            for v in result['custom_relationships']},
    }
