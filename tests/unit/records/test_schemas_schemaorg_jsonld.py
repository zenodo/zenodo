# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Unit tests Zenodo JSON-LD serializer."""

from __future__ import absolute_import, print_function

from datetime import datetime

from flask_security import login_user

from zenodo.modules.records.serializers import schemaorg_jsonld_v1
from zenodo.modules.records.serializers.schemaorg import \
    ZenodoSchemaOrgSerializer
from zenodo.modules.records.serializers.schemas import schemaorg

SCHEMA_ORG_TYPES = [
    ('poster', None, schemaorg.CreativeWork),
    ('presentation', None, schemaorg.PresentationDigitalDocument),
    ('dataset', None, schemaorg.Dataset),
    ('image', 'figure', schemaorg.ImageObject),
    ('image', 'plot', schemaorg.ImageObject),
    ('image', 'drawing', schemaorg.ImageObject),
    ('image', 'diagram', schemaorg.ImageObject),
    ('image', 'photo', schemaorg.Photograph),
    ('image', 'other', schemaorg.ImageObject),
    ('video', None, schemaorg.MediaObject),
    ('software', None, schemaorg.SoftwareSourceCode),
    ('lesson', None, schemaorg.CreativeWork),
    ('other', None, schemaorg.CreativeWork),
    ('publication', 'book', schemaorg.Book),
    ('publication', 'section', schemaorg.ScholarlyArticle),
    ('publication', 'conferencepaper', schemaorg.ScholarlyArticle),
    ('publication', 'article', schemaorg.ScholarlyArticle),
    ('publication', 'patent', schemaorg.CreativeWork),
    ('publication', 'preprint', schemaorg.ScholarlyArticle),
    ('publication', 'report', schemaorg.ScholarlyArticle),
    ('publication', 'softwaredocumentation', schemaorg.CreativeWork),
    ('publication', 'thesis', schemaorg.ScholarlyArticle),
    ('publication', 'technicalnote', schemaorg.ScholarlyArticle),
    ('publication', 'workingpaper', schemaorg.ScholarlyArticle),
    ('publication', 'proposal', schemaorg.CreativeWork),
    ('publication', 'deliverable', schemaorg.CreativeWork),
    ('publication', 'milestone', schemaorg.CreativeWork),
    ('publication', 'other', schemaorg.CreativeWork),
]


def test_serializer(minimal_record_model, recid_pid):
    """Test the schema.org JSON-LD serializer."""
    out = schemaorg_jsonld_v1.serialize(recid_pid, minimal_record_model)


def test_schema_class_resolver():
    """Test the Marshmallow schema class based on different resource types."""
    for type_, subtype, schema_class in SCHEMA_ORG_TYPES:
        obj = {'metadata': {'resource_type': {'type': type_}}}
        if subtype:
            obj['metadata']['resource_type']['subtype'] = subtype
        cls = ZenodoSchemaOrgSerializer._get_schema_class(obj)
        assert schema_class == cls


def test_person():
    """Test the schema.org Person schema."""
    simple_person = {'name': 'Doe, John'}
    data, err = schemaorg.Person().dump(simple_person)
    assert not err
    assert data == {'name': 'Doe, John', '@type': 'Person'}
    simple_person['affiliation'] = 'CERN'

    data, err = schemaorg.Person().dump(simple_person)
    assert not err
    assert data == {'name': 'Doe, John',
                    'affiliation': 'CERN',
                    '@type': 'Person'}

    # Add GND - it should become the identifier of the person
    simple_person['gnd'] = '170118215'

    data, err = schemaorg.Person().dump(simple_person)
    assert not err
    assert data == {'name': 'Doe, John',
                    'affiliation': 'CERN',
                    '@type': 'Person',
                    '@id': 'http://d-nb.info/gnd/170118215'}

    # Add ORCID - it should supercede GND as the identifier
    simple_person['orcid'] = '0000-0002-1825-0097'
    data, err = schemaorg.Person().dump(simple_person)
    assert not err
    assert data == {'name': 'Doe, John',
                    'affiliation': 'CERN',
                    '@type': 'Person',
                    '@id': 'https://orcid.org/0000-0002-1825-0097'}

    # Remove GND
    del simple_person['gnd']
    data, err = schemaorg.Person().dump(simple_person)
    assert not err
    assert data == {'name': 'Doe, John',
                    'affiliation': 'CERN',
                    '@type': 'Person',
                    '@id': 'https://orcid.org/0000-0002-1825-0097'}


def test_language():
    """Test the schema.org Language schema."""
    lang = 'pol'
    data, err = schemaorg.Language().dump(lang)
    assert not err
    assert data == {'alternateName': 'pol',
                    '@type': 'Language',
                    'name': 'Polish'}


def test_minimal_software_record(minimal_record_model):
    """Test the minimal record model dumping."""
    minimal_record_model['related_identifiers'] = [
        {
          "identifier": "https://github.com/orgname/reponame/tree/v0.1.0",
          "relation": "isSupplementTo",
          "scheme": "url"
        }
    ]
    data, err = schemaorg.SoftwareSourceCode().dump(
        dict(metadata=minimal_record_model))
    assert not err
    expected = {
        u'@context': u'https://schema.org/',
        u'@id': 'https://doi.org/10.5072/zenodo.123',
        u'@type': u'SoftwareSourceCode',
        u'url': 'http://localhost/record/123',
        u'description': u'My description',
        u'codeRepository': 'https://github.com/orgname/reponame/tree/v0.1.0',
        u'creator': [
            {
                u'@type': u'Person',
                u'name': u'Test'
            }
        ],
        u'datePublished': datetime.utcnow().date().isoformat(),
        u'name': u'Test'}
    assert data == expected


def test_full_record(record_with_files_creation):
    """Test the full record model dumping."""
    recid, record, _ = record_with_files_creation
    # full_record fixture is a "book"
    schema_cls = ZenodoSchemaOrgSerializer._get_schema_class(
        dict(metadata=record))
    assert schema_cls == schemaorg.Book
    data, err = schemaorg.ScholarlyArticle().dump(dict(metadata=record))
    assert not err
    expected = {
        u'@context': u'https://schema.org/',
        u'@id': 'https://doi.org/10.1234/foo.bar',
        u'@type': u'Book',
        u'about': [
            {
                u'@id': u'http://id.loc.gov/authorities/subjects/sh85009003',
                u'@type': u'CreativeWork'
            }
        ],
        u'citation': [
            {
                u'@id': 'https://doi.org/10.1234/foo.bar',
                u'@type': u'CreativeWork'
            },
            {
                u'@id': 'http://arxiv.org/abs/arXiv:1234.4321',
                u'@type': u'CreativeWork'
            },
            {
                '@id': 'http://arxiv.org/abs/arXiv:1234.4328',
                '@type': 'CreativeWork'
            }
        ],
        u'contributor': [
            {
                u'@id': 'https://orcid.org/0000-0002-1825-0097',
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Smith, Other'
            },
            {
                u'@type': u'Person',
                u'affiliation': u'',
                u'name': u'Hansen, Viggo'
            },
            {
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Kowalski, Manager'
            }
        ],
        u'creator': [
            {
                u'@id': 'https://orcid.org/0000-0002-1694-233X',
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Doe, John'
            },
            {
                u'@id': 'https://orcid.org/0000-0002-1825-0097',
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Doe, Jane'
            },
            {
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Smith, John'
            },
            {
                u'@id': 'http://d-nb.info/gnd/170118215',
                u'@type': u'Person',
                u'affiliation': u'CERN',
                u'name': u'Nowak, Jack'
            }
        ],
        u'datePublished': '2014-02-27',
        u'description': u'Test Description',
        u'headline': u'Test title',
        u'image':
            u'https://zenodo.org/static/img/logos/zenodo-gradient-round.svg',
        u'inLanguage': {
            u'@type': u'Language',
            u'alternateName': u'eng',
            u'name': u'English'
        },
        u'sameAs': [
            u'http://arxiv.org/abs/arXiv:1234.4325',
            u'http://adsabs.harvard.edu/abs/2011ApJS..192...18K',
            u'https://doi.org/10.1234/alternate.doi',
        ],
        u'isPartOf': [
            {
                u'@id': 'https://doi.org/10.1234/zenodo.4321',
                u'@type': u'CreativeWork'
            }
        ],
        u'hasPart': [
            {
                u'@id': 'https://doi.org/10.1234/zenodo.1234',
                u'@type': u'CreativeWork'
            }
        ],
        u'keywords': [u'kw1', u'kw2', u'kw3'],
        u'license': u'https://creativecommons.org/licenses/by/4.0/',
        u'name': u'Test title',
        u'url': u'http://localhost/record/12345',
        u'version': u'1.2.5'
    }
    assert data == expected


def test_dataset_with_files(app, users, minimal_record_model, recid_pid):
    """Testing the dumping of files in Open Access datasets."""
    with app.test_request_context():
        datastore = app.extensions['security'].datastore
        login_user(datastore.get_user(users[0]['email']))
        assert minimal_record_model['access_right'] == 'open'
        minimal_record_model['resource_type'] = dict(type='dataset')
        minimal_record_model['_files'] = [
            {
                'bucket': '22222222-2222-2222-2222-222222222222',
                'version_id': '11111111-1111-1111-1111-111111111111',
                'file_id': '22222222-3333-4444-5555-666666666666',
                'checksum': 'md5:11111111111111111111111111111111',
                'key': 'test',
                'size': 4,
                'type': 'txt',
            },
            {
                'bucket': '22222222-2222-2222-2222-222222222222',
                'version_id': '11111111-1111-1111-1111-111111111112',
                'file_id': '22222222-3333-4444-5555-666666666667',
                'checksum': 'md5:11111111111111111111111111111112',
                'key': 'test2',
                'size': 1000000,
                'type': 'pdf',
            },
        ]

        data, err = schemaorg.Dataset().dump(
            dict(metadata=minimal_record_model))
        assert not err
        assert data['distribution'] == [
            {
                u'@type': u'DataDownload',
                u'contentUrl': u'https://https://zenodo.org/api/files/'
                               u'22222222-2222-2222-2222-222222222222/test',
                u'fileFormat': u'txt'
            },
            {
                u'@type': u'DataDownload',
                u'contentUrl': u'https://https://zenodo.org/api/files/'
                               u'22222222-2222-2222-2222-222222222222/test2',
                u'fileFormat': u'pdf'
            }
        ]
        for right in ['closed', 'embargoed', 'restricted']:

            minimal_record_model['access_right'] = right
            data, err = schemaorg.Dataset().dump(
                dict(metadata=minimal_record_model))
            assert not err
            assert 'distribution' not in data
