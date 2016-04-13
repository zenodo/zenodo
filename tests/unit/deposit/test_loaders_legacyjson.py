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

from invenio_deposit.api import Deposit
from zenodo.modules.deposit.loaders import legacyjson_translator


def t(**kwargs):
    """Simple helper to translate small part of legacy JSON."""
    return legacyjson_translator(dict(metadata=kwargs))


def defaults(**kwargs):
    """Simple helper to translate small part of legacy JSON."""
    d = {
        '$schema': (
            'https://zenodo.org/schemas/deposits/records/record-v1.0.0.json')}
    d.update(kwargs)
    return d


def test_direct_mapping():
    """Test fields that maps directly."""
    fields = [
        'publication_date', 'title', 'description', 'notes', 'embargo_date',
        'access_right', 'thesis_university', 'doi', 'access_conditions']

    for f in fields:
        assert t(**{f: 'TEST'}) == defaults(**{f: 'TEST'})


def test_resource_type():
    """Test DOI translation."""
    assert t(upload_type='software') == \
        defaults(resource_type=dict(type='software'))
    assert t(upload_type='publication', publication_type='preprint') == \
        defaults(resource_type=dict(type='publication', subtype='preprint'))
    assert t(upload_type='image', image_type='photo') == \
        defaults(resource_type=dict(type='image', subtype='photo'))
    assert t(
        upload_type='publication', image_type='photo',
        publication_type='preprint') == \
        defaults(resource_type=dict(type='publication', subtype='preprint'))
    assert t(
        upload_type='invalid') == \
        defaults(resource_type=dict(type='invalid'))


def test_creators_supervisors():
    """Test creators and thesis supervisors."""
    for k in ['creators', 'thesis_supervisors']:
        assert t(**{k: [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215"),
            dict(name="Smith, Jane", affiliation="Atlantis")
        ]}) == defaults(**{k: [
            dict(name="Doe, John", affiliation="Atlantis",
                 orcid="0000-0002-1825-0097", gnd="170118215"),
            dict(name="Smith, Jane", affiliation="Atlantis")
        ]})


def test_contributors():
    """Test contributors."""
    assert t(**{'contributors': [
        dict(name="Doe, John", affiliation="Atlantis",
             orcid="0000-0002-1825-0097", gnd="170118215",
             type="DataCurator"),
        dict(name="Smith, Jane", affiliation="Atlantis", type="Other")
    ]}) == defaults(**{'contributors': [
        dict(name="Doe, John", affiliation="Atlantis",
             orcid="0000-0002-1825-0097", gnd="170118215",
             type="DataCurator"),
        dict(name="Smith, Jane", affiliation="Atlantis", type="Other")
    ]})


def test_keywords():
    """Test keywords."""
    assert t(keywords=['kw1', 'kw2']) == defaults(keywords=['kw1', 'kw2'])


def test_subjects():
    """Test subjects."""
    assert t(subjects=[{
        "term": "Astronomy",
        "id": "http://id.loc.gov/authorities/subjects/sh85009003",
        "scheme": "url"
    }]) == defaults(subjects=[{
        "term": "Astronomy",
        "identifier": "http://id.loc.gov/authorities/subjects/sh85009003",
        "scheme": "url"
    }])

    assert t(subjects=[{
        "term": "Astronomy",
        "id": "http://id.loc.gov/authorities/subjects/sh85009003",
    }]) == defaults(subjects=[{
        "term": "Astronomy",
        "identifier": "http://id.loc.gov/authorities/subjects/sh85009003",
    }])


def test_related_alternate_identifiers():
    """Test related alternate identifiers."""
    assert t(related_identifiers=[
        dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
        dict(identifier='10.1234/foo.bar3', relation='cites', scheme='doi'),
        dict(
            identifier='2011ApJS..192...18K',
            relation='isAlternativeIdentifier'),
        dict(
            identifier='2011ApJS..192...18K',
            relation='isAlternativeIdentifier',
            scheme='ads'),
    ]) == defaults(
        related_identifiers=[
            dict(
                identifier='10.1234/foo.bar2', relation='isCitedBy',
                scheme='doi'),
            dict(
                identifier='10.1234/foo.bar3', relation='cites', scheme='doi'),
        ],
        alternate_identifiers=[
            dict(
                identifier='2011ApJS..192...18K', scheme='ads'),
            dict(
                identifier='2011ApJS..192...18K',
                scheme='ads'),
        ],
    )


def test_references():
    """Test references."""
    assert t(references=[
        "Reference 1",
        "Reference 2",
    ]) == defaults(references=[
        dict(raw_reference="Reference 1"),
        dict(raw_reference="Reference 2"),
    ])


def test_journal():
    """Test journal."""
    assert t(
        journal_issue="Some issue",
        journal_pages="Some pages",
        journal_title="Some journal name",
        journal_volume="Some volume",
    ) == defaults(journal=dict(
        issue="Some issue",
        pages="Some pages",
        title="Some journal name",
        volume="Some volume",
    ))


def test_meetings():
    """Test meetings."""
    assert t(
        conference_acronym='Some acronym',
        conference_dates='Some dates',
        conference_place='Some place',
        conference_title='Some title',
        conference_url='http://someurl.com',
        conference_session='VI',
        conference_session_part='1',
    ) == defaults(meetings=dict(
        acronym='Some acronym',
        dates='Some dates',
        place='Some place',
        title='Some title',
        url='http://someurl.com',
        session='VI',
        session_part='1',
    ))


def test_imprint():
    """Test part of vs imprint."""
    assert t(
        imprint_isbn="Some isbn",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
    ) == defaults(imprint=dict(
        isbn="Some isbn",
        place="Some place",
        publisher="Some publisher",
    ))
    assert t(
        publication_date="2016-01-01",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
    ) == defaults(
        imprint=dict(
            year="2016",
            place="Some place",
            publisher="Some publisher"
        ),
        publication_date="2016-01-01"
    )


def test_partof():
    """Test part of vs imprint."""
    assert t(
        partof_pages="Some pages",
        partof_title="Some title",
    ) == defaults(part_of=dict(
        pages="Some pages",
        title="Some title",
    ))
    assert t(
        partof_pages="Some pages",
        partof_title="Some title",
        publication_date="2016-01-01",
        imprint_place="Some place",
        imprint_publisher="Some publisher",
        imprint_isbn="Some isbn",
    ) == defaults(
        part_of=dict(
            year="2016",
            place="Some place",
            publisher="Some publisher",
            isbn="Some isbn",
            pages="Some pages",
            title="Some title",
        ),
        publication_date="2016-01-01"
    )


def test_license():
    """Test license."""
    assert t(
        license="cc-zero",
    ) == defaults(
        license={'$ref': 'https://dx.zenodo.org/licenses/cc-zero'}
    )


def test_grants():
    """Test license."""
    assert t(
        grants=[dict(id='283595'), dict(id='10.13039/501100000780::643410')],
    ) == defaults(
        grants=[
            {'$ref': (
                'https://dx.zenodo.org/grants/10.13039/501100000780::283595'
            )},
            {'$ref': (
                'https://dx.zenodo.org/grants/10.13039/501100000780::643410'
            )},
        ]
    )


def test_communities():
    """Test communities."""
    assert t(
        communities=[dict(identifier='ecfunded')],
    ) == defaults(
        communities=['ecfunded']
    )


def test_prereserve_doi():
    """Test communities."""
    assert t(
        prereserve_doi=True,
    ) == defaults(_deposit_actions=dict(prereserve_doi=True))


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
            embargo_date="2010-12-09",
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
    Deposit.create(legacyjson_translator(test_data)).validate()
