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

from datetime import timedelta

import arrow

from zenodo.modules.records.serializers import legacyjson_v1

legacyjson_v1.replace_refs = False


def test_id(minimal_record_model, depid_pid):
    """Test created."""
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['id'] == int(depid_pid.pid_value)


def test_created_modified(minimal_record_model, depid_pid):
    """Test created."""
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert arrow.get(obj['created']) <= arrow.utcnow()
    assert arrow.get(obj['modified']) <= arrow.utcnow()


def test_doi(minimal_record_model, depid_pid):
    """Test created."""
    minimal_record_model['doi'] = '10.1234/foo'
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['doi'] == '10.1234/foo'
    assert obj['doi_url'] == 'https://doi.org/10.1234/foo'


def test_owners(minimal_record_model, depid_pid):
    """Test created."""
    minimal_record_model['owners'] = [1, 2, 3]
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['owner'] == 1


def test_owners_deposit(minimal_record_model, depid_pid):
    """Test owners."""
    minimal_record_model['_deposit'] = dict(owners=[3, 2, 1])
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['owner'] == 3


def test_recid(minimal_record_model, depid_pid):
    """Test recid."""
    # TODO: Record URL.
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['record_id'] == 123
    del minimal_record_model['recid']
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert 'record_id' not in obj


def test_title(minimal_record_model, depid_pid):
    """Test title."""
    minimal_record_model['title'] = 'TEST'
    obj = legacyjson_v1.transform_record(depid_pid, minimal_record_model)
    assert obj['title'] == 'TEST'
    assert obj['metadata']['title'] == 'TEST'


def test_upload_type(minimal_record_model, depid_pid):
    """Test upload/publication/image type."""
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['upload_type'] == 'software'
    assert 'publication_type' not in obj
    assert 'image_type' not in obj

    minimal_record_model['resource_type'] = dict(
        type='publication', subtype='preprint')
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['upload_type'] == 'publication'
    assert obj['publication_type'] == 'preprint'
    assert 'image_type' not in obj

    minimal_record_model['resource_type'] = dict(
        type='image', subtype='photo')
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['upload_type'] == 'image'
    assert obj['image_type'] == 'photo'
    assert 'publication_type' not in obj


def test_publication_date(minimal_record_model, depid_pid):
    """Test publication date."""
    for k in ['publication_date', 'embargo_date']:
        minimal_record_model[k] = arrow.utcnow().date() - timedelta(days=1)
        obj = legacyjson_v1.transform_record(
            depid_pid, minimal_record_model)['metadata']
        assert arrow.get(obj[k]).date() <= arrow.utcnow().date()


def test_creators(minimal_record_model, depid_pid):
    """Test creators."""
    minimal_record_model['creators'] = [
        {'name': 'Doe, John', 'affiliation': '', 'orcid': '',
         'familyname': 'Doe', 'givennames': 'John'},
        {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '1234',
         'familyname': 'Smith', 'givennames': 'John', 'gnd': '4321'},
    ]
    minimal_record_model['thesis'] = dict(
        supervisors=minimal_record_model['creators']
    )
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['creators'] == [
        {'name': 'Doe, John'},
        {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '1234',
         'gnd': '4321', },
    ]
    assert obj['thesis_supervisors'] == obj['creators']


def test_contributors(minimal_record_model, depid_pid):
    """Test contributors."""
    minimal_record_model['contributors'] = [
        {'name': 'Doe, John', 'affiliation': '', 'orcid': '',
         'familyname': 'Doe', 'givennames': 'John', 'type': 'DataCurator'},
        {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '1234',
         'familyname': 'Smith', 'givennames': 'John', 'gnd': '4321',
         'type': 'Other'},
    ]
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['contributors'] == [
        {'name': 'Doe, John', 'type': 'DataCurator'},
        {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '1234',
         'gnd': '4321', 'type': 'Other'},
    ]


def test_direct_mappings(minimal_record_model, depid_pid):
    """Test direct mappings."""
    fields = [
        'title', 'description', 'notes', 'access_right', 'access_conditions'
    ]

    for f in fields:
        minimal_record_model[f] = 'TEST'
        obj = legacyjson_v1.transform_record(
            depid_pid, minimal_record_model)['metadata']
        assert obj[f] == 'TEST'


def test_thesis_university(minimal_record_model, depid_pid):
    """Test direct mappings."""
    minimal_record_model['thesis'] = dict(university='TEST')
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['thesis_university'] == 'TEST'


def test_prereserve(minimal_record_model, depid_pid):
    """Test prereserve DOI."""
    minimal_record_model['_deposit_actions'] = dict(prereserve_doi=True)
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['prereserve_doi'] == {
        'recid': 123,
        'doi': '10.5072/zenodo.123'
    }


def test_keywords(minimal_record_model, depid_pid):
    """Test keywords."""
    kws = ['kw1', 'kw2']
    minimal_record_model['keywords'] = kws
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['keywords'] == kws


def test_references(minimal_record_model, depid_pid):
    """Test references."""
    refs = [{'raw_reference': 'ref1'}, {'raw_reference': 'ref2'}]
    minimal_record_model['references'] = refs
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['references'] == ['ref1', 'ref2']


def test_communities(minimal_record_model, depid_pid):
    """Test communities."""
    minimal_record_model['communities'] = ['zenodo']
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['communities'] == [{'identifier': 'zenodo'}]


def test_journal(minimal_record_model, depid_pid):
    """Test journal."""
    minimal_record_model['journal'] = {
        'title': 'Mathematical Combinations',
        'volume': '1',
        'issue': 'V',
        'pages': '141',
        'year': '2000',
    }
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['journal_title']
    assert obj['journal_volume']
    assert obj['journal_issue']
    assert obj['journal_pages']
    assert 'journal_year' not in obj


def test_conference(minimal_record_model, depid_pid):
    """Test conferences."""
    minimal_record_model['meeting'] = {
        'title': '20th International Conference on Computing in High Energy '
                 'and Nuclear Physics',
        'acronym': 'CHEP\'13',
        'dates': '14-18 October 2013',
        'place': 'Amsterdam, The Netherlands',
        'url': 'http://www.chep2013.org/',
        'session': 'VI',
        'session_part': '1'
    }
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['conference_title']
    assert obj['conference_acronym']
    assert obj['conference_dates']
    assert obj['conference_place']
    assert obj['conference_url']
    assert obj['conference_session']
    assert obj['conference_session_part']


def test_related_identifiers(minimal_record_model, depid_pid):
    """Test related identifiers."""
    minimal_record_model.update(dict(
        related_identifiers=[
            dict(identifier='10.1234/f', scheme='doi', relation='cites'),
        ],
        alternate_identifiers=[
            dict(identifier='10.1234/f', scheme='doi'),
        ],
    ))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['related_identifiers'] == [
        dict(identifier='10.1234/f', scheme='doi', relation='cites'),
        dict(identifier='10.1234/f', scheme='doi',
             relation='isAlternateIdentifier'),
    ]


def test_grants(minimal_record_model, depid_pid):
    """Test grants."""
    minimal_record_model.update(dict(grants=[
        dict(
            internal_id='10.13039/501100000780::282896',
            funder=dict(
                doi='10.13039/501100000780',
                name='European Commission',
                acronyms=['EC'],
            ),
            identifiers=dict(
                eurepo='info:eu-repo/grantAgreement/EC/FP7/282896',
            ),
            code='282896',
            title='Open Access Research Infrastructure in Europe',
            acronym='OpenAIREplus',
            program='FP7',
        ),
        dict(
            internal_id='10.13039/501100000780::643410',
            funder=dict(
                doi='10.13039/501100000780',
                name='European Commission',
                acronyms=['EC'],
            ),
            identifiers=dict(
                eurepo='info:eu-repo/grantAgreement/EC/H2020/643410',
            ),
            code='643410',
            title='Open Access Infrastructure for Research in Europe 2020',
            acronym='OpenAIRE2020',
            program='H2020',
        ),
    ]))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['grants'] == [
        dict(id='282896'),
        dict(id='10.13039/501100000780::643410'),
    ]


def test_license(minimal_record_model, depid_pid):
    """Test license."""
    minimal_record_model.update(dict(license=dict(id='CC0-1.0')))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['license'] == 'CC0-1.0'


def test_subjects(minimal_record_model, depid_pid):
    """Test subjects."""
    minimal_record_model.update(dict(subjects=[
        dict(
            term="Astronomy",
            identifier="http://id.loc.gov/authorities/subjects/sh85009003",
            scheme="url"
        ),
    ]))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']
    assert obj['subjects'] == [
        dict(
            term="Astronomy",
            id="http://id.loc.gov/authorities/subjects/sh85009003",
            scheme="url"
        ),
    ]


def test_imprint(minimal_record_model, depid_pid):
    """Test imprint."""
    minimal_record_model.update(dict(
        imprint=dict(
            place='Some place',
            publisher='Some publisher',
            isbn='978-3-16-148410-0',
        ),
    ))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']

    assert 'imprint_publisher' in obj
    assert 'imprint_place' in obj
    assert 'imprint_isbn' in obj
    assert 'imprint_year' not in obj


def test_partof(minimal_record_model, depid_pid):
    """Test imprint."""
    minimal_record_model.update(dict(
        imprint=dict(
            place='Some place',
            publisher='Some publisher',
            isbn='Some isbn',
        ),
        part_of=dict(
            pages="Some pages",
            title="Some title",
        ),
    ))

    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)['metadata']

    assert 'imprint_publisher' in obj
    assert 'imprint_place' in obj
    assert 'imprint_isbn' in obj
    assert 'partof_pages' in obj
    assert 'partof_title' in obj
    assert 'imprint_year' not in obj
    assert 'partof_year' not in obj


def test_state(minimal_record_model, depid_pid):
    """Test state."""
    minimal_record_model.update(dict(
        _deposit=dict(status='draft')
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['state'] == 'unsubmitted'

    minimal_record_model.update(dict(
        _deposit=dict(
            status='draft',
            pid={u'revision_id': 0, u'type': u'recid', u'value': u'1'}
        )
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['state'] == 'inprogress'

    minimal_record_model.update(dict(
        _deposit=dict(status='published')
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['state'] == 'done'

    del minimal_record_model['_deposit']['status']
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['state'] == 'unsubmitted'

    minimal_record_model.update(dict(
        _deposit=dict(
            pid={u'revision_id': 0, u'type': u'recid', u'value': u'1'}
        )
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['state'] == 'inprogress'


def test_submitted(minimal_record_model, depid_pid):
    """Test state."""
    minimal_record_model.update(dict(
        _deposit=dict(status='draft')
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['submitted'] is False

    minimal_record_model.update(dict(
        _deposit=dict(status='published')
    ))
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['submitted'] is True

    del minimal_record_model['_deposit']['status']
    obj = legacyjson_v1.transform_record(
        depid_pid, minimal_record_model)
    assert obj['submitted'] is False
