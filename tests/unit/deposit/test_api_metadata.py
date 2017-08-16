# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Test validation in Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import json
from datetime import datetime, timedelta

from flask import url_for
from invenio_search import current_search
from six import BytesIO


def test_invalid_create(api_client, es, json_auth_headers, deposit_url,
                        get_json):
    """Test invalid deposit creation."""
    client = api_client
    headers = json_auth_headers

    # Invalid deposits.
    cases = [
        dict(unknownkey='data', metadata={}),
        dict(metadat={}),
    ]

    for case in cases:
        res = client.post(deposit_url, data=json.dumps(case), headers=headers)
        assert res.status_code == 400, case

    # No deposits were created
    assert 0 == len(
        get_json(client.get(deposit_url, headers=headers), code=200))


def test_input_output(api_client, es, json_auth_headers, deposit_url, get_json,
                      license_record, grant_record, locations):
    """Rough validation of input against output data."""
    client = api_client
    headers = json_auth_headers

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
                datetime.utcnow().date() + timedelta(days=1)).isoformat(),
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
                dict(scheme="gnd", identifier="gnd:1234567899",
                     term="Astronaut"),
                dict(scheme="gnd", identifier="gnd:1234567898", term="Amish"),
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
                dict(identifier='10.1234/foo.bar2', relation='isCitedBy',
                     scheme='doi'),
                dict(identifier='10.1234/foo.bar3', relation='cites',
                     scheme='doi'),
                dict(
                    identifier='2011ApJS..192...18K',
                    relation='isAlternateIdentifier',
                    scheme='ads'),
            ],
            thesis_supervisors=[
                dict(name="Doe Sr., John", affiliation="Atlantis"),
                dict(name="Smith Sr., Jane", affiliation="Atlantis",
                     orcid="0000-0002-1825-0097",
                     gnd="170118215")
            ],
            thesis_university="Some thesis_university",
            contributors=[
                dict(name="Doe Sr., Jochen", affiliation="Atlantis",
                     type="Other"),
                dict(name="Smith Sr., Marco", affiliation="Atlantis",
                     orcid="0000-0002-1825-0097",
                     gnd="170118215",
                     type="DataCurator")
            ],
            title="Test title",
            upload_type="publication",
        )
    )

    # Create
    res = client.post(deposit_url, data=json.dumps(test_data), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Get serialization.
    data = get_json(client.get(links['self'], headers=headers), code=200)
    # - fix known differences.
    # DOI and recid have 2 as control number, since Concept DOI/recid are
    # registered first
    test_data['metadata'].update({
        'prereserve_doi': {'doi': '10.5072/zenodo.2', 'recid': 2}
    })
    assert data['metadata'] == test_data['metadata']


def test_unicode(api_client, es, locations, json_auth_headers, deposit_url,
                 get_json, license_record, grant_record, auth_headers,
                 communities):
    """Rough validation of input against output data."""
    client = api_client
    headers = json_auth_headers

    test_data = dict(
        metadata=dict(
            access_right='open',
            access_conditions='Αυτή είναι μια δοκιμή',
            communities=[{'identifier': 'c1'}],
            conference_acronym='Αυτή είναι μια δοκιμή',
            conference_dates='هذا هو اختبار',
            conference_place='Սա փորձություն',
            conference_title='Гэта тэст',
            conference_url='http://someurl.com',
            conference_session='5',
            conference_session_part='a',
            creators=[
                dict(name="Doe, John", affiliation="Това е тест"),
                dict(name="Smith, Jane", affiliation="Tio ĉi estas testo")
            ],
            description="这是一个测试",
            doi="10.1234/foo.bar",
            embargo_date="2010-12-09",
            grants=[dict(id="282896"), ],
            imprint_isbn="Some isbn",
            imprint_place="這是一個測試",
            imprint_publisher="ეს არის გამოცდა",
            journal_issue="આ એક કસોટી છે",
            journal_pages="זהו מבחן",
            journal_title="यह एक परीक्षण है",
            journal_volume="Þetta er prófun",
            keywords=["これはテストです", "ಇದು ಪರೀಕ್ಷೆ"],
            subjects=[
                dict(scheme="gnd", identifier="1234567899", term="これはです"),
                dict(scheme="gnd", identifier="1234567898", term="ಇ"),
            ],
            license="CC0-1.0",
            notes="이것은 테스트입니다",
            partof_pages="ນີ້ແມ່ນການທົດສອບ",
            partof_title="ही चाचणी आहे",
            prereserve_doi=True,
            publication_date="2013-09-12",
            publication_type="book",
            related_identifiers=[
                dict(
                    identifier='2011ApJS..192...18K',
                    relation='isAlternativeIdentifier'),
                dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                dict(identifier='10.1234/foo.bar3', relation='cites'),
            ],
            thesis_supervisors=[
                dict(name="Doe Sr., این یک تست است", affiliation="Atlantis"),
                dict(name="Это Sr., Jane", affiliation="Atlantis")
            ],
            thesis_university="இந்த ஒரு சோதனை",
            contributors=[
                dict(name="Doe Sr.,  ن یک تست", affiliation="Atlantis",
                     type="Other"),
                dict(name="SmЭтith Sr., Marco", affiliation="Atlantis",
                     type="DataCurator")
            ],
            title="Đây là một thử nghiệm",
            upload_type="publication",
        )
    )

    # Create
    res = client.post(deposit_url, data=json.dumps(test_data), headers=headers)
    links = get_json(res, code=201)['links']
    current_search.flush_and_refresh(index='deposits')

    # Upload  file
    assert client.post(
        links['files'],
        data=dict(file=(BytesIO(b'test'), 'test.txt'), name='test.txt'),
        headers=auth_headers,
    ).status_code == 201

    # Publish deposition
    response = client.post(links['publish'], headers=auth_headers)
    record_id = get_json(response, code=202)['record_id']

    # Get record.
    current_search.flush_and_refresh(index='records')
    response = client.get(
        url_for('invenio_records_rest.recid_item', pid_value=record_id))


def test_validation(api_client, es, json_auth_headers, deposit_url, get_json,
                    license_record, grant_record, auth_headers):
    """Test validation."""
    client = api_client
    headers = json_auth_headers

    test_data = dict(metadata=dict(
        access_right='notvalid',
        conference_url='not_a_url',
        doi='not a doi',
        publication_date='not a date',
        title='',
        upload_type='notvalid'
    ))

    data = get_json(
        client.post(deposit_url, data=json.dumps(test_data), headers=headers),
        code=400)

    field_errors = {e['field'] for e in data['errors']}
    expected_field_errors = set([
        'metadata.access_right',
        'metadata.conference_url',
        'metadata.doi',
        'metadata.publication_date',
        'metadata.title',
        'metadata.upload_type',
    ])

    for e in expected_field_errors:
        assert e in field_errors
