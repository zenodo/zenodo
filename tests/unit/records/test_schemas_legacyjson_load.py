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

"""Unit tests Zenodo legacy JSON deserializer."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import pytest
from flask import Flask
from marshmallow.exceptions import ValidationError

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.records.serializers.schemas.legacyjson import \
    LegacyMetadataSchemaV1, LegacyRecordSchemaV1


def d(**kwargs):
    """Default data."""
    defaults = dict(
        publication_date=datetime.utcnow().date().isoformat(),
        title='Title',
        description='Description',
        upload_type='software',
    )
    defaults.update(kwargs)
    return defaults


@pytest.mark.parametrize('val, expected', [
    (' Test ', 'Test'),
    ('TEST', 'TEST'),
])
def test_title(val, expected):
    """Test titles."""
    assert LegacyMetadataSchemaV1(strict=True).load(
        d(title=val)).data['title'] == expected


@pytest.mark.parametrize('val', [
    '   ',
    ' 12  ',
    None
])
def test_title_invalid(val):
    """Test invalid titles."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(title=val)
    )


def test_upload_type():
    """Test upload type deserialization."""
    s = LegacyMetadataSchemaV1(
        partial=['upload_type', 'publication_type', 'image_type'],
        strict=True
    )
    s.load(d(
        upload_type='publication',
        publication_type='book',
    )).data['resource_type'] == {'subtype': 'book', 'type': 'publication'}
    # Irrelevant extra key.
    s.load(d(
        upload_type='image',
        publication_type='book',
        image_type='photo',
    )).data['resource_type'] == {'subtype': 'photo', 'type': 'image'}


def test_upload_type_invalid():
    """Test upload type deserialization."""
    s = LegacyMetadataSchemaV1(strict=True)

    # Missing value
    obj = d()
    obj.pop('upload_type')
    pytest.raises(ValidationError, s.load, obj)

    # Invalid value
    obj.update(dict(upload_type='invalid'))
    pytest.raises(ValidationError, s.load, obj)

    # Missing subtype
    obj.update(dict(upload_type='publication'))
    pytest.raises(ValidationError, s.load, obj)

    # Invalid subtype
    obj.update(dict(upload_type='image', image_type='invalid'))
    pytest.raises(ValidationError, s.load, obj)


def test_related_alternate_identifiers():
    """Test related alternate identifiers."""
    s = LegacyMetadataSchemaV1(strict=True)

    result = s.load(d(related_identifiers=[
        dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
        dict(identifier='10.1234/foo.bar3', relation='cites', scheme='doi'),
        dict(
            identifier='2011ApJS..192...18K',
            relation='isAlternateIdentifier'),   # Name difference on purpose
        dict(
            identifier='2011ApJS..192...18K',
            relation='isAlternativeIdentifier',  # Name difference on purpose
            scheme='ads'),
    ]))
    assert result.data['related_identifiers'] == [
        dict(
            identifier='10.1234/foo.bar2', relation='isCitedBy',
            scheme='doi'),
        dict(
            identifier='10.1234/foo.bar3', relation='cites', scheme='doi'),
    ]
    assert result.data['alternate_identifiers'] == [
        dict(
            identifier='2011ApJS..192...18K', scheme='ads'),
        dict(
            identifier='2011ApJS..192...18K',
            scheme='ads'),
    ]


@pytest.mark.parametrize('relation', [
    'IsCitedBy',
    'invalid',
    None
])
def test_related_identifiers_invalid_relations(relation):
    """Test invalid related identifiers."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(related_identifiers=[
            dict(identifier='10.1234/foo.bar2', relation=relation),
        ])
    )


def test_related_identifiers_invalid():
    """Test missing relation."""
    s = LegacyMetadataSchemaV1(strict=True).load
    # Missing relation
    pytest.raises(ValidationError, s, d(related_identifiers=[
        dict(identifier='10.1234/foo.bar2'),
    ]))
    # Invalid scheme
    pytest.raises(ValidationError, s, d(related_identifiers=[
        dict(identifier='10.1234/foo.bar2', scheme='isbn'),
    ]))
    # Invalid scheme
    pytest.raises(ValidationError, s, d(related_identifiers=[
        dict(identifier='10.1234/foo.bar2', scheme='invalid'),
    ]))
    # Missing identifier
    pytest.raises(ValidationError, s, d(related_identifiers=[
        dict(scheme='doi', relation='isCitedBy'),
    ]))


@pytest.mark.parametrize('input, output, scheme', [
    ('https://doi.org/10.1234/foo.bar2', '10.1234/foo.bar2', None),
])
def test_related_identifiers_normalization(input, output, scheme):
    """Test missing relation."""
    assert LegacyMetadataSchemaV1(strict=True).load(d(related_identifiers=[
        dict(identifier=input, relation='isCitedBy', scheme=scheme)
    ])).data['related_identifiers'][0]['identifier'] == output


def test_creators():
    """Test creators."""
    s = LegacyMetadataSchemaV1(strict=True)

    assert s.load(d(creators=[
        dict(name="Doe, John", affiliation="Atlantis",
             orcid="0000-0002-1825-0097", gnd="170118215"),
        dict(name="Smith, Jane", affiliation="Atlantis")
    ])).data['creators'] == [
        dict(name="Doe, John", affiliation="Atlantis",
             orcid="0000-0002-1825-0097", gnd="170118215"),
        dict(name="Smith, Jane", affiliation="Atlantis")
    ]

    # Min length required
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(creators=[])
    )


@pytest.mark.parametrize('creator', [
    dict(name="Doe, John", orcid="invalid"),
    dict(name="", affiliation="Atlantis"),
    dict(name="Doe, John", gnd="invalid"),
])
def test_creators_invalid(creator):
    """Test creators."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(creators=[creator])
    )


@pytest.mark.parametrize('date', [
    '2013-05-08',
    '1855-05-08',
    '0001-01-01',
])
def test_publication_date(date):
    """Test creators."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(
        d(publication_date=date)
    ).data['publication_date'] == date


@pytest.mark.parametrize('date', [
    '2013-02-32',
    'invalid',
    None,
    {'a dict': ''}
])
def test_publication_date_invalid(date):
    """Test creators."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(publication_date=date)
    )


@pytest.mark.parametrize('desc, expected', [
    ('My description', None),
    ('<b>HTML test</b>', None),
    ('<a href="http://localhost.dk" style="background: black;">HTML test</b>',
     '<a href="http://localhost.dk">HTML test</a>'),
    ('   My description   ', 'My description'),
    (' <a href="javascript:evil_function()">a link</a> ', '<a>a link</a>'),
    ('<p onclick="evil_function()">a paragraph</p>', '<p>a paragraph</p>'),
])
def test_description(desc, expected):
    """Test descriptions.

    Note, we only do limited sanitize test because we use the bleach library
    to sanitize and it already have extensive tests.
    """
    assert LegacyMetadataSchemaV1(strict=True).load(
        d(description=desc)
    ).data['description'] == (expected or desc)


@pytest.mark.parametrize('desc', [
    '    ',
    '12',
    ' <script></script> ',
])
def test_description_invalid(desc):
    """Test invalid description."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(description=desc)
    )


@pytest.mark.parametrize('desc, expected', [
    ('My notes', 'My notes'),
    (' My notes ', 'My notes'),
])
def test_notes(desc, expected):
    """Test notes."""
    assert LegacyMetadataSchemaV1(strict=True).load(
        d(notes=desc)
    ).data['notes'] == expected


@pytest.mark.parametrize('desc', [
    None,
    124,
])
def test_notes_invalid(desc):
    """Test invalid notes."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(notes=desc)
    )


def test_keywords():
    """Test keywords."""
    assert LegacyMetadataSchemaV1(strict=True).load(
        d(keywords=['kw1', ' kw2 ', ' '])
    ).data['keywords'] == ['kw1', 'kw2']


@pytest.mark.parametrize('keywords', [
    [None],
    [124, ],
    [{'mykw': ''}],
    {'adict': 'instead of list'},
])
def test_keywords_invalid(keywords):
    """Test invalid keywords."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(keywords=keywords)
    )


@pytest.mark.parametrize('val', [
    123,
    'OPEN',
    'invalid',
    ' open ',
])
def test_access_rights_invalid(val):
    """Test creators."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(access_right=val)
    )


@pytest.mark.parametrize('val, removedkeys', [
    ('open', ['embargo_date', 'access_conditions']),
    ('embargoed', ['access_conditions']),
    ('restricted', ['license', 'embargo_date', ]),
    ('closed', ['license', 'embargo_date', 'access_conditions']),
])
def test_access_rights(val, removedkeys):
    """Test access rights."""
    data = dict(
        license='cc-by',
        embargo_date=(
            datetime.utcnow() + timedelta(days=2)).date().isoformat(),
        access_conditions='TEST'
    )

    result = LegacyMetadataSchemaV1(strict=True).load(
        d(access_right=val, **data)
    )
    assert result.data['access_right'] == val
    # Make sure removed keys **are not** in output
    for k in removedkeys:
        assert k not in result.data
    # Make sure non-removed keys **are** in output
    for k in (set(data.keys()) - set(removedkeys)):
        assert k in result.data


@pytest.mark.parametrize('dt', [
    '2013-05-08',
    '2100-01-00',
])
def test_embargo_date_invalid(dt):
    """Test embargo date."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(access_right='embargoed', embargo_date=dt)
    )


@pytest.mark.parametrize('desc, expected', [
    ('My description', None),
    ('<b>HTML test</b>', None),
    ('<a href="http://localhost.dk" style="background: black;">HTML test</b>',
     '<a href="http://localhost.dk">HTML test</a>'),
    ('   My description   ', 'My description'),
    (' <a href="javascript:evil_function()">a link</a> ', '<a>a link</a>'),
    ('<p onclick="evil_function()">a paragraph</p>', '<p>a paragraph</p>'),
])
def test_acess_conditions(desc, expected):
    """Test access conditions."""
    assert LegacyMetadataSchemaV1(strict=True).load(
        d(access_right='restricted', access_conditions=desc)
    ).data['access_conditions'] == (expected or desc)


@pytest.mark.parametrize('input_val', [
    '10.1234/foo.bar',
    'http://dx.doi.org/10.1234/foo.bar',
    'https://doi.org/10.1234/foo.bar',
    ' doi:10.1234/foo.bar ',
    ' 10.1234/foo.bar ',
])
def test_valid_doi(input_val):
    """Test DOI."""
    data, errors = LegacyMetadataSchemaV1(partial=['doi'], strict=True).load(
        d(doi=input_val))
    assert data['doi'] == '10.1234/foo.bar'


def test_subjects():
    """Test subjects."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(subjects=[{
        "term": "Astronomy",
        "id": "http://id.loc.gov/authorities/subjects/sh85009003",
        "scheme": "url"
    }])).data['subjects'] == [{
        "term": "Astronomy",
        "identifier": "http://id.loc.gov/authorities/subjects/sh85009003",
        "scheme": "url"
    }]
    assert s.load(d(subjects=[{
        "term": "Astronomy",
        # We allow to use both 'id' and 'identifier'
        "identifier": "http://id.loc.gov/authorities/subjects/sh85009003",
    }])).data['subjects'] == [{
        "term": "Astronomy",
        "identifier": "http://id.loc.gov/authorities/subjects/sh85009003",
        "scheme": "url"
    }]


def test_contributors():
    """Test contributors."""
    app = Flask(__name__)
    app.config.update(dict(DEPOSIT_CONTRIBUTOR_DATACITE2MARC=dict(
        Other='...',
        DataCurator='...',
    )))
    s = LegacyMetadataSchemaV1(strict=True)
    with app.app_context():
        assert s.load(d(**{'contributors': [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215",
                 type="DataCurator"),
            dict(name="Smith, Jane", affiliation="Atlantis", type="Other")
        ]})).data['contributors'] == [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215",
                 type="DataCurator"),
            dict(name="Smith, Jane", affiliation="Atlantis", type="Other")
        ]


@pytest.mark.parametrize('contributor', [
    dict(name="Doe, John", orcid="invalid", type='Other'),
    dict(name="", affiliation="Atlantis", type='Other'),
    dict(name="Doe, John", gnd="invalid", type='Other'),
    dict(name="Doe, John"),
])
def test_contributors_invalid(contributor):
    """Test creators."""
    app = Flask(__name__)
    app.config.update(dict(DEPOSIT_CONTRIBUTOR_DATACITE2MARC=dict(
        Other='...',
        DataCurator='...',
    )))
    with app.app_context():
        pytest.raises(
            ValidationError,
            LegacyMetadataSchemaV1(strict=True).load,
            d(contributors=[contributor])
        )


def test_references():
    """Test references."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(references=[
        "Reference 1",
        "  ",
        "Reference 2",
    ])).data['references'] == [
        dict(raw_reference="Reference 1"),
        dict(raw_reference="Reference 2"),
    ]


def test_thesis():
    """Test creators and thesis supervisors."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(**{
        'thesis_supervisors': [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215"),
            dict(name="Smith, Jane", affiliation="Atlantis")
        ],
        'thesis_university': 'Important'
    })).data['thesis'] == {
        'supervisors': [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215"),
            dict(name="Smith, Jane", affiliation="Atlantis")
        ],
        'university': 'Important',
    }


def test_journal():
    """Test journal."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        journal_issue="Some issue",
        journal_pages="Some pages",
        journal_title="Some journal name",
        journal_volume="Some volume",
    )).data['journal'] == dict(
        issue="Some issue",
        pages="Some pages",
        title="Some journal name",
        volume="Some volume",
    )


def test_meetings():
    """Test meetings."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        conference_acronym='Some acronym',
        conference_dates='Some dates',
        conference_place='Some place',
        conference_title='Some title',
        conference_url='http://someurl.com',
        conference_session='VI',
        conference_session_part='1',
    )).data['meeting'] == dict(
        acronym='Some acronym',
        dates='Some dates',
        place='Some place',
        title='Some title',
        url='http://someurl.com',
        session='VI',
        session_part='1',
    )


def test_imprint():
    """Test part of vs imprint."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        imprint_isbn="Some isbn",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
    )).data['imprint'] == dict(
        isbn="Some isbn",
        place="Some place",
        publisher="Some publisher",
    )
    assert s.load(d(
        publication_date="2016-01-01",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
    )).data['imprint'] == dict(
        place="Some place",
        publisher="Some publisher"
    )


def test_partof():
    """Test part of vs imprint."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        partof_pages="Some pages",
        partof_title="Some title",
    )).data['part_of'] == dict(
        pages="Some pages",
        title="Some title",
    )
    result = s.load(d(
        partof_pages="Some pages",
        partof_title="Some title",
        publication_date="2016-01-01",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
        imprint_isbn="Some isbn",
    ))
    assert result.data['part_of'] == dict(
        pages="Some pages",
        title="Some title",
    )
    assert result.data['imprint'] == dict(
        place="Some place",
        publisher="Some publisher",
        isbn="Some isbn",
    )


def test_prereserve_doi():
    """Test license."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert 'prereserve_doi' not in s.load(d(
        prereserve_doi=True
    )).data


def test_license():
    """Test license."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        access_right='open', license="cc-zero"
    )).data['license'] == {
        '$ref': 'https://dx.zenodo.org/licenses/cc-zero'
    }


def test_grants():
    """Test grants."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        grants=[dict(id='283595'), dict(id='10.13039/501100000780::643410')],
    )).data['grants'] == [
        {'$ref': (
            'https://dx.zenodo.org/grants/10.13039/501100000780::283595'
        )},
        {'$ref': (
            'https://dx.zenodo.org/grants/10.13039/501100000780::643410'
        )},
    ]


def test_communities():
    """Test communities."""
    s = LegacyMetadataSchemaV1(strict=True)
    assert s.load(d(
        communities=[
            dict(identifier='zenodo'), dict(), dict(identifier='ecfunded'),
        ],
    )).data['communities'] == ['ecfunded', 'zenodo']


@pytest.mark.parametrize('comms', [
    1234,
    [1234],
    'zenodo',
    {'dict': 'test'}
])
def test_communities_invalid(comms):
    """Test communities."""
    pytest.raises(
        ValidationError,
        LegacyMetadataSchemaV1(strict=True).load,
        d(communities=comms)
    )


def test_legacyjson_to_record_translation(app, db, es, grant_record,
                                          license_record):
    """Test the translator legacy_zenodo and zenodo_legacy."""
    test_data = dict(
        metadata=dict(
            access_right='embargoed',
            communities=[{'identifier': 'cfa'}],
            conference_acronym='Some acronym',
            conference_dates='Some dates',
            conference_place='Some place',
            conference_title='Some title',
            conference_url='http://someurl.com',
            conference_session='VI',
            conference_session_part='1',
            creators=[
                dict(name="Doe, John", affiliation="Atlantis",
                     orcid="0000-0002-1825-0097", gnd="170118215"),
                dict(name="Smith, Jane", affiliation="Atlantis")
            ],
            description="Some description",
            doi="10.1234/foo.bar",
            embargo_date=(
                datetime.utcnow().date() + timedelta(days=2)).isoformat(),
            grants=[dict(id="282896"), ],
            imprint_isbn="Some isbn",
            imprint_place="Some place",
            imprint_publisher="Some publisher",
            journal_issue="Some issue",
            journal_pages="Some pages",
            journal_title="Some journal name",
            journal_volume="Some volume",
            keywords=["Keyword 1", "keyword 2"],
            subjects=[
                dict(scheme="gnd", identifier="1234567899", term="Astronaut"),
                dict(scheme="gnd", identifier="1234567898", term="Amish"),
            ],
            license="CC0-1.0",
            notes="Some notes",
            partof_pages="SOme part of",
            partof_title="Some part of title",
            prereserve_doi=True,
            publication_date="2013-09-12",
            publication_type="book",
            references=[
                "Reference 1",
                "Reference 2",
            ],
            related_identifiers=[
                dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                dict(identifier='10.1234/foo.bar3', relation='cites'),
                dict(
                    identifier='2011ApJS..192...18K',
                    relation='isAlternativeIdentifier'),
            ],
            thesis_supervisors=[
                dict(name="Doe Sr., John", affiliation="Atlantis"),
                dict(name="Smith Sr., Jane", affiliation="Atlantis",
                     orcid="http://orcid.org/0000-0002-1825-0097",
                     gnd="http://d-nb.info/gnd/170118215")
            ],
            thesis_university="Some thesis_university",
            contributors=[
                dict(name="Doe Sr., Jochen", affiliation="Atlantis",
                     type="Other"),
                dict(name="Smith Sr., Marco", affiliation="Atlantis",
                     orcid="http://orcid.org/0000-0002-1825-0097",
                     gnd="http://d-nb.info/gnd/170118215",
                     type="DataCurator")
            ],
            title="Test title",
            upload_type="publication",
        )
    )
    ZenodoDeposit.create(
        LegacyRecordSchemaV1(strict=True).load(test_data).data
    ).validate()
