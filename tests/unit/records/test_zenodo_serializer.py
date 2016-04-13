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

    schema = PersonSchemaV1()

    data = {
        'name': 'Doe, John',
        'affiliation': 'Zenodo',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'name': 'Smith, Jane',
        'affiliation': 'Zenodo',
        'orcid': '0000-0002-1694-233X',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'name': 'Kowalski, Jack',
        'affiliation': 'Zenodo',
        'gnd': '170118215',
    }
    result = schema.load(data)
    assert result.data == data


def test_contributor_schema():
    """Test ContributorSchemaV1."""

    schema = ContributorSchemaV1()

    data = {
        'name': 'Doe, John',
        'affiliation': 'Zenodo',
        'type': 'Editor',
    }
    result = schema.load(data)
    assert result.data == data


def test_community_schema():
    """Test CommunitySchemaV1."""

    schema = CommunitySchemaV1()

    data = {
        'identifier': 'ecfunded',
    }
    result = schema.load(data)
    assert result.data == data


def test_conference_schema():
    """Test ConferenceSchemaV1."""

    schema = ConferenceSchemaV1()

    data = {
        'title': '20th International Conference on Computing in High Energy '
                 'and Nuclear Physics',
        'acronym': 'CHEP\'13',
        'dates': '14-18 October 2013',
        'place': 'Amsterdam, The Netherlands',
        'url': 'http://www.chep2013.org/',
        'session': 'VI',
    }
    result = schema.load(data)
    assert result.data == data


def test_grant_schema():
    """Test GrantSchemaV1."""

    schema = GrantSchemaV1()

    data = {
        'id': '283595',
    }
    result = schema.load(data)
    assert result.data == data


def test_imprint_schema():
    """Test ImprintSchemaV1."""

    schema = ImprintSchemaV1()

    data = {
        'publisher': 'invenio',
        'isbn': '978-3-16-148410-0',
        'place': 'invenio',
    }
    result = schema.load(data)
    assert result.data == data


def test_journal_schema():
    """Test JournalSchemaV1."""

    schema = JournalSchemaV1()

    data = {
        'title': 'Mathematical Combinations',
        'volume': '1',
        'issue': 'none',
        'pages': '141',
    }
    result = schema.load(data)
    assert result.data == data


def test_partof_schema():
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

    schema = RelatedIdentifierSchemaV1()

    data = {
        'relation': 'isSupplementTo',
        'identifier': '10.1234/foo',
    }
    result = schema.load(data)
    assert result.data == data

    data = {
        'relation': 'cites',
        'identifier': 'http://dx.doi.org/10.1234/bar',
    }
    result = schema.load(data)
    assert result.data == data


def test_thesis_schema():
    """Test ThesisSchemaV1."""

    schema = ThesisSchemaV1()

    data = {
        'supervisors': [
            {
                'name': 'Kowalski, Jack',
                'affiliation': 'Zenodo',
                'gnd': '170118215',
                'orcid': '0000-0002-1694-233X',
            },
        ],
        'university': 'University U',
    }
    result = schema.load(data)
    assert result.data == data


def test_subject_schema():
    """Test SubjectSchemaV1."""

    schema = SubjectSchemaV1()

    data = {
        'term': 'Astronomy',
        'id': 'http://id.loc.gov/authorities/subjects/sh85009003',
        'scheme': 'url',
    }
    result = schema.load(data)
    assert result.data == data


deposition_metadata_data = {
    'upload_type': 'publication',
    'publication_type': 'book',
    'image_type': 'figure',
    'publication_date': '2000-01-01',
    'title': 'Title of deposition',
    'creators': [
        {
            'name': 'Doe, John',
            'affiliation': 'Zenodo',
        },
        {
            'name': 'Smith, Jane',
            'affiliation': 'Zenodo',
            'orcid': '0000-0002-1694-233X',
        },
        {
            'name': 'Kowalski, Jack',
            'affiliation': 'Zenodo',
            'gnd': '170118215',
        },
    ],
    'description': '<p>Abstract or description for deposition.</p>',
    'access_right': 'embargoed',
    'license': 'cc-by',
    'embargo_date': '2000-01-01',
    'access_conditions': '',
    'doi': '10.5281/zenodo.16745',
    'prereserve_doi': True,
    'keywords': [
        'Keyword 1',
        'Keyword 2',
    ],
    'notes': 'No additional notes.',
    'related_identifiers': [
        {
            'relation': 'isSupplementTo',
            'identifier': '10.1234/foo',
        },
        {
            'relation': 'cites',
            'identifier': 'http://dx.doi.org/10.1234/bar',
        }
    ],
    'contributors': [
        {
            'name': 'Doe, John',
            'affiliation': 'Zenodo',
            'type': 'Editor',
        },
    ],
    'references': [
        "Doe J (2014). Title. Publisher. DOI",
        "Smith J (2014). Title. Publisher. DOI",
    ],
    'communities': [
        {
            'identifier': 'ecfunded',
        },
    ],
    'grants': [
        {
            'id': '283595',
        },
    ],
    'journal_title': 'Mathematical Combinations',
    'journal_volume': '1',
    'journal_issue': 'none',
    'journal_pages': '141',
    'conference_title': '20th International Conference on Computing in'
                        ' High Energy and Nuclear Physics',
    'conference_acronym': 'CHEP\'13',
    'conference_dates': '14-18 October 2013',
    'conference_place': 'Amsterdam, The Netherlands',
    'conference_url': 'http://www.chep2013.org/',
    'conference_session': 'VI',
    'imprint_publisher': 'invenio',
    'imprint_isbn': '978-3-16-148410-0',
    'imprint_place': 'invenio',
    'partof_title': 'Title',
    'partof_pages': '10',
    'thesis_supervisors': [
        {
            'name': 'Kowalski, Jack',
            'affiliation': 'Zenodo',
            'gnd': '170118215',
            'orcid': '0000-0002-1694-233X',
        },
    ],
    'thesis_university': 'University U',
    'subjects': [
        {
            'term': 'Astronomy',
            'id': 'http://id.loc.gov/authorities/subjects/sh85009003',
            'scheme': 'url',
        },
    ]
}


def test_deposition_metadata_deserializer():
    """Test ZenodoDepositionMetadataSchemaV1."""

    schema = ZenodoDepositionMetadataSchemaV1()

    data = deposition_metadata_data
    result = schema.load(data)
    assert result.data == data


def test_deposition_file_schema():
    """Test ZenodoMetadataSchemaV1."""

    schema = ZenodoDepositionFileSchemaV1()

    data = {
        'id': 'identifier',
        'filename': 'file.id',
        'filesize': 1234567890,
        'checksum': 'ASDF',
    }
    result = schema.load(data)
    assert result.data == data


def test_deposition_deserializer():
    """Test ZenodoDepositionSchemaV1."""

    schema = ZenodoDepositionSchemaV1()

    data = {
        'created': '2000-01-01',
        'doi': '10.5281/zenodo.16745',
        'doi_url': 'https://localhost/',
        'files': [
            {
                'id': 'identifier',
                'filename': 'file.id',
                'filesize': 1234567890,
                'checksum': 'ASDF',
            }
        ],
        'id': 1,
        'metadata': deposition_metadata_data,
        'modified': '2000-01-01',
        'owner': 1,
        'record_id': 2,
        'record_url': 'https://localhost/',
        'state': 'done',
        'submitted': True,
        'title': '2000-01-01',
    }
    result = schema.load(data)
    assert result.data == data


def test_deposition_serialization_deserialization():
    """Test ZenodoMetadataDeposition serialization deserialization."""

    schema = ZenodoDepositionMetadataSchemaV1()

    data = {
        'creators': [
            {
                'affiliation': 'Zenodo',
                'name': 'Doe, John'
            }
        ],
        'description': 'This is my first upload',
        'title': 'My first upload'
    }
    result = schema.load(data)
    assert result.data == data
