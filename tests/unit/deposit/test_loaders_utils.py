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

from zenodo.modules.deposit.loaders.utils import filter_empty_list, \
    filter_thesis, is_valid, none_if_empty


def test_is_nonempty():
    """Test legacy JSON cleaning functions."""
    is_valid_f1 = is_valid(keys=['name', 'affiliation'])

    assert is_valid_f1({'name': 'Doe, John', 'affiliation': 'CERN'})
    assert is_valid_f1({'name': 'Doe, John', 'orcid': '1234-1234-1234'})
    assert is_valid_f1({'affiliation': 'CERN', 'orcid': '1234-1234-1234'})
    assert not is_valid_f1({'gnd': '123451235', 'orcid': '1234-1234-1234'})
    assert is_valid_f1({'name': '', 'affiliation': 'CERN'})
    assert is_valid_f1({'name': 'Doe, John', 'affiliation': ''})
    assert not is_valid_f1({'name': '', 'affiliation': ''})
    assert not is_valid_f1({'name': [], 'affiliation': {}})
    assert not is_valid_f1({'name': None, 'affiliation': None})
    assert is_valid_f1(1)
    assert is_valid_f1(0)
    assert not is_valid_f1({})
    assert not is_valid_f1([])
    assert not is_valid_f1(None)
    assert not is_valid_f1('')

    is_valid_f2 = is_valid()
    assert is_valid_f2({'name': 'Doe, John', 'affiliation': 'CERN'})
    assert is_valid_f2({'name': 'Doe, John', 'orcid': '1234-1234-1234'})
    assert is_valid_f2({'affiliation': 'CERN', 'orcid': '1234-1234-1234'})
    assert is_valid_f2({'gnd': '123451235', 'orcid': '1234-1234-1234'})
    assert is_valid_f1(1)
    assert is_valid_f1(0)
    assert not is_valid_f2({})
    assert not is_valid_f2([])
    assert not is_valid_f2(None)
    assert not is_valid_f2('')


def test_filter_list():
    """Test legacy JSON cleaning functions."""
    d1 = {
        'contributors': [
            {  # Should stay
                'name': 'Doe, John the 1st',
                'affiliation': 'CERN',
            },
            {  # Should stay
                'name': 'Doe, John the 2nd',
                'affiliation': '',
            },
            {  # Should stay
                'name': 'Doe, John the 3rd',
            },
            {  # Should stay
                'name': '',
                'affiliation': 'CERN',
            },
            {  # Should be removed
                'orcid': '1234-1234-1234',
                'name': '',
                'affiliation': '',
            },
            {  # Should be removed
                'name': '',
                'affiliation': '',
                'orcid': '1234-1234-1234',
                'gnd': '12341234',
            }
        ],
        'subjects': [
            {
                'identifier': 'FooID1',
                'term': 'FooTerm1',
                'scheme': 'FooScheme1',
            },
            {
                'term': 'FooTerm2',
            },
            {
                'identifier': 'FooID2',
                'scheme': 'FooScheme1',
            },
        ],
    }
    exp_d1 = {
        'contributors': [
            {  # Should stay
                'name': 'Doe, John the 1st',
                'affiliation': 'CERN',
            },
            {  # Should stay
                'name': 'Doe, John the 2nd',
                'affiliation': '',
            },
            {  # Should stay
                'name': 'Doe, John the 3rd',
            },
            {  # Should stay
                'name': '',
                'affiliation': 'CERN',
            },
        ],
        'subjects': [
            {
                'identifier': 'FooID1',
                'term': 'FooTerm1',
                'scheme': 'FooScheme1',
            },
            {
                'term': 'FooTerm2',
            },
        ]
    }

    assert filter_empty_list(keys=['name', 'affiliation'])(
        d1['contributors']) == exp_d1['contributors']
    assert filter_empty_list(keys=['term'])(
        d1['subjects']) == exp_d1['subjects']

    d2 = {
        'related_identifiers': [
            {
                'scheme': '',
                'relation': 'isSupplementTo',
                'identifier': ' arXiv:1601.08082'
            },
            {
                'scheme': '',
                'relation': 'isSupplementTo',
                'identifier': 'hello',
            },
            {
                'scheme': '',
                'relation': 'isSupplementTo',
                'identifier': 'arXiv:1601_.08082'
            },
            {
                'scheme': 'arxiv',
                'relation': 'isSupplementTo',
                'identifier': 'arXiv:1601.08082'
            },
            {
                'scheme': 'arxiv',
                'relation': 'isSupplementTo',
                'identifier': ''
            },
            {
                'scheme': 'arxiv',
                'relation': 'isSupplementTo',
            },
        ]
    }
    exp_d2 = {
        'related_identifiers': [
            {
                'relation': 'isSupplementTo',
                'identifier': ' arXiv:1601.08082'
            },
            {
                'relation': 'isSupplementTo',
                'identifier': 'hello',
            },
            {
                'relation': 'isSupplementTo',
                'identifier': 'arXiv:1601_.08082'
            },
            {
                'scheme': 'arxiv',
                'relation': 'isSupplementTo',
                'identifier': 'arXiv:1601.08082'
            },
        ]
    }
    func1 = filter_empty_list(keys=['identifier', ], remove_empty_keys=True)
    assert func1(d2['related_identifiers']) == exp_d2['related_identifiers']


def test_none_if_empty():
    """Test filtering out empty elements."""
    journal_filter = none_if_empty(keys=['title'])
    d1 = {
        'journal': {
            'issue': '1',
            'pages': '123-234',
            'title': 'Foobar',
            'volume': '1',
            'year': '2001'
        }
    }
    exp_d1 = {
        'journal': {
            'issue': '1',
            'pages': '123-234',
            'title': 'Foobar',
            'volume': '1',
            'year': '2001'
        }
    }

    assert journal_filter(d1['journal']) == \
        exp_d1['journal']

    d2 = {
        'journal': {
            'issue': '1',
            'pages': '123-234',
            'volume': '1',
            'year': '2001'
        }
    }
    d3 = {
        'journal': {
            'issue': '1',
            'pages': '123-234',
            'title': '',
            'volume': '1',
            'year': '2001'
        }
    }

    assert journal_filter(d2['journal']) is None
    assert journal_filter(d3['journal']) is None


def test_filter_thesis():
    """Test thesis filtering."""
    filter_thesis_func = filter_thesis(keys=['name', 'affiliation'])
    d1 = {
        'thesis': {
            'supervisors': [
                {
                    'name': 'Doe, John',
                    'affiliation': 'CERN',
                },
                {
                    'name': 'Doe, Jane',
                    'affiliation': 'CERN',
                },
            ],
            'university': 'University of Foo',
        }
    }
    exp_d1 = dict(d1)
    assert filter_thesis_func(d1['thesis']) == exp_d1['thesis']
    d2 = {
        'thesis': {
            'supervisors': [
                {
                    'name': '',
                    'affiliation': 'CERN',
                },
                {
                    'name': 'Doe, Jane',
                    'affiliation': '',
                },
            ],
            'university': '',
        }
    }
    exp_d2 = {
        'thesis': {
            'supervisors': [
                {
                    'name': '',
                    'affiliation': 'CERN',
                },
                {
                    'name': 'Doe, Jane',
                    'affiliation': '',
                },
            ],
        }
    }
    assert filter_thesis_func(d2['thesis']) == exp_d2['thesis']
    d3 = {
        'thesis': {
            'supervisors': [
                {
                    'name': '',
                    'orcid': '1234-1234-1234',
                },
                {
                    'name': 'Doe, Jane',
                    'affiliation': '',
                },
            ],
        }
    }
    exp_d3 = {
        'thesis': {
            'supervisors': [
                {
                    'name': 'Doe, Jane',
                    'affiliation': '',
                },
            ],
        }
    }
    assert filter_thesis_func(d3['thesis']) == exp_d3['thesis']
    d4 = {
        'thesis': {
            'university': 'Foobar',
        }
    }
    exp_d4 = {
        'thesis': {
            'university': 'Foobar',
        }
    }
    assert filter_thesis_func(d4['thesis']) == exp_d4['thesis']
    d5 = {
        'thesis': {
            'supervisors': [
                {
                    'name': '',
                    'orcid': '1234-1234-1234',
                },
                {
                    'name': '',
                    'affiliation': '',
                },
            ],
            'university': '',
        }
    }
    exp_d5 = {
        'thesis': {}
    }
    assert filter_thesis_func(d5['thesis']) == exp_d5['thesis']
