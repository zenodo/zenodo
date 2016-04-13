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

"""Unit tests Zenodo serializer legacy."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.serializers.schemas.zenodo import *


def test_person_schema():
    """Test PersonSchemaV1."""

    schema = ZenodoPersonSchemaV1()

    data = {
        'name': 'Doe, John',
        'familyname': 'Doe',
        'givennames': 'John',
        'affiliation': 'Zenodo',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'name': 'Smith, Jane',
        'affiliation': 'Zenodo',
        'familyname': 'Smith',
        'givennames': 'Jave',
        'orcid': '0000-0002-1694-233X',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'name': 'Kowalski, Jack',
        'affiliation': 'Zenodo',
        'familyname': 'Kowalski',
        'givennames': 'Jack',
        'gnd': '170118215',
    }
    result = schema.load(data)
    assert result.data == data


def test_contributor_schema():
    """Test ContributorSchemaV1."""

    schema = ZenodoContributorSchemaV1()

    data = {
        'name': 'Doe, John',
        'affiliation': 'Zenodo',
        'type': 'Editor',
        'familyname': 'Doe',
        'givennames': 'John',
    }
    result = schema.load(data)
    assert result.data == data


def test_conference_schema():
    """Test ConferenceSchemaV1."""

    schema = ZenodoMeetingSchemaV1()

    data = {
        'title': '20th International Conference on Computing in High Energy '
                 'and Nuclear Physics',
        'acronym': 'CHEP\'13',
        'dates': '14-18 October 2013',
        'place': 'Amsterdam, The Netherlands',
        'url': 'http://www.chep2013.org/',
        'session': 'VI',
        'session_part': 'I',
    }
    result = schema.load(data)
    assert result.data == data


def test_imprint_schema():
    """Test ImprintSchemaV1."""

    schema = ZenodoImprintSchemaV1()

    data = {
        'publisher': 'invenio',
        'place': 'invenio',
    }
    result = schema.load(data)
    assert result.data == data


def test_journal_schema():
    """Test JournalSchemaV1."""

    schema = ZenodoJournalSchemaV1()

    data = {
        'title': 'Mathematical Combinations',
        'volume': '1',
        'issue': 'none',
        'pages': '141',
        'year': '1999',
    }
    result = schema.load(data)
    assert result.data == data


def test_part_of_schema():
    """Test PartOfSchemaV1."""

    schema = PartOfSchemaV1()

    data = {
        'title': 'Title',
        'pages': '10',
    }
    result = schema.load(data)
    assert result.data == data


def test_related_identifiers_schema():
    """Test RelatedIdentifiersSchemaV1."""

    schema = ZenodoRelatedIdentifierSchemaV1()

    data = {
        'relation': 'isSupplementTo',
        'identifier': '10.1234/foo',
        'scheme': 'A',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'relation': 'cites',
        'identifier': 'http://dx.doi.org/10.1234/bar',
        'scheme': 'A',
    }
    result = schema.load(data)
    assert result.data == data


def test_alternate_identifiers_schema():
    """Test RelatedIdentifiersSchemaV1."""

    schema = ZenodoRelatedIdentifierSchemaV1()

    data = {
        'identifier': '10.1234/foo',
        'scheme': 'A',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'identifier': 'http://dx.doi.org/10.1234/bar',
        'scheme': 'A',
    }
    result = schema.load(data)
    assert result.data == data


def test_subject_schema():
    """Test SubjectSchemaV1."""

    schema = ZenodoSubjectSchemaV1()

    data = {
        'term': 'Astronomy',
        'identifier': 'http://id.loc.gov/authorities/subjects/sh85009003',
        'scheme': 'url',
    }
    result = schema.load(data)
    assert result.data == data


def test_deposition_file_schema():
    """Test ZenodoMetadataSchemaV1."""

    schema = ZenodoDepositionFileSchemaV1()

    data = {
        'bucket': '1',
        'filename': 'file.id',
        'version_id': '1',
        'size': 1234567890,
        'checksum': 'ASDF',
        'previewer': 'id',
        'type': 'ID',
    }
    result = schema.load(data)
    assert result.data == data


def test_deposition_deserializer():
    """Test ZenodoDepositionSchemaV1."""

    schema = ZenodoRecordSchemaV1()

    data = {
        'doi': '10.1234/foo',
        'isbn': '10.5281/zenodo.16745',
        'altmetric_id': 'aaa',
        'resource_type': {
            'type': 'publication',
            'subtype': 'book',
        },
        'publication_date': '2000-01-01',
        'publication_type': 'book',
        'title': 'Title',
        'creators': [
            {
                'name': 'Doe, John',
                'affiliation': 'Zenodo',
                'familyname': 'Doe',
                'givennames': 'John',
            },
            {
                'name': 'Smith, Jane',
                'affiliation': 'Zenodo',
                'familyname': 'Jane',
                'givennames': 'Smith',
                'orcid': '0000-0002-1694-233X',
            },
            {
                'name': 'Kowalski, Jack',
                'familyname': 'Kowalski',
                'givennames': 'Jack',
                'affiliation': 'Zenodo',
                'gnd': '170118215',
            },
        ],
        'description': 'Emtpy description.',
        'keywords': ['KeywordA', 'KeywordB'],
        'subjects': [
            {
                'term': 'Astronomy',
                'identifier': 'http://id.loc.gov/authorities/subjects/sh85003',
                'scheme': 'url',
            },
        ],
        'notes': 'No notes',
        'access_right': 'embargoed',
        'embargo_date': '2000-01-01',
        'access_conditions': '',  # TODO access_conditions
        'license': {
            'identifier': 'li-li',
            'license': 'License Li',
            'source': 'Bla',
            'url': 'http://localhost/',
        },
        'communities': [
            'ecfunded',
        ],
        'provisional_communities': [
            'ecfunded2',
        ],
        'grants': [
            '283595'
        ],
        'related_identifiers': [
            {
                'relation': 'isSupplementTo',
                'identifier': '10.1234/foo',
                'scheme': 'scheme',
            },
        ],
        'alternate_identifiers': [
            {
                'scheme': 'scheme',
                'identifier': '10.1234/foo',
            },
        ],
        'contributors': [
            {
                'name': 'Doe, John',
                'affiliation': 'Zenodo',
                'familyname': 'Doe',
                'givennames': 'John',
            },
        ],
        'references': [
            {
                'raw_reference': 'Doe J (2014). Title. Publisher. DOI',
            },
            {
                'raw_reference': 'Smith J (2014). Title. Publisher. DOI',
            },
        ],
        'journal': {
            'title': 'Mathematical Combinations',
            'volume': '1',
            'issue': 'none',
            'pages': '141',
            'year': '2000'
        },
        'meetings': {
            'title': '20th International Conference on Computing in High'
                     ' Energy and Nuclear Physics',
            'acronym': 'CHEP\'13',
            'dates': '14-18 October 2013',
            'place': 'Amsterdam, The Netherlands',
            'url': 'http://www.chep2013.org/',
            'session': 'VI',
            'session_part': 'I',
        },
        'part_of': {
            'title': 'Title',
            'pages': '10',
            'publisher': 'invenio',
            'place': 'invenio',
            'isbn': '10.5281/zenodo.16745',
            'year': '2000',
        },
        'imprint': {
            'publisher': 'invenio',
            'place': 'invenio',
        },
        'thesis_university': 'Univeristy U',
        'thesis_supervisors': [
             {
                'name': 'Doe, John',
                'affiliation': 'Zenodo',
                'familyname': 'Doe',
                'givennames': 'John',
             },
        ],
        'files': [
            {
                'bucket': 'Bu',
                'filename': 'Bu.bu',
                'version_id': 'V1',
                'size': 1,
                'checksum': 'bla',
                'previewer': 'Bu',
                'type': 'bu',
            }
        ],
        'owners': [1, 2],
    }
    result = schema.load(data)
    assert result.data == data
