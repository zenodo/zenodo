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
from invenio_search import current_search


def test_input_output(api_client, deposit, json_auth_headers,
                      deposit_url, get_json, license_record, grant_record):
    """Test data validation."""
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
    # Fix known differences.
    test_data['metadata'].update({
        'prereserve_doi': {'doi': '10.5072/zenodo.1', 'recid': 1}
    })
    assert data['metadata'] == test_data['metadata']
