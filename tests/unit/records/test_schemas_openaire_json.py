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

"""Zenodo CSL mapping test."""

from __future__ import absolute_import, print_function

import pytest
from invenio_records.api import Record

from zenodo.modules.records.serializers import openaire_json_v1


@pytest.fixture()
def minimal_oai_record(minimal_record):
    """Minimal OAI record."""
    minimal_record['_oai'] = {
        'id': 'oai:zenodo.org:{}'.format(minimal_record['recid'])
    }
    minimal_record['resource_type'] = {
        'type': 'publication',
        'subtype': 'article'
    }
    return minimal_record


def test_minimal(app, db, minimal_oai_record, recid_pid):
    """Test minimal record."""
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj == {
        'originalId': 'oai:zenodo.org:123',
        'type': 'publication',
        'resourceType': '0001',
        'title': 'Test',
        'licenseCode': 'OPEN',
        'url': 'https://zenodo.org/record/123',
        'authors': ['Test'],
        'description': 'My description',
        'pids': [{'type': 'oai', 'value': 'oai:zenodo.org:123'}],
        'hostedById': 'opendoar____::2659',
        'collectedFromId': 'opendoar____::2659',
    }


def test_resource_types(app, db, minimal_oai_record, recid_pid):
    """"Test resource types."""
    minimal_oai_record['doi'] = '10.1234/foo'

    minimal_oai_record.update({'resource_type': {'type': 'dataset'}})
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    # Datasets use the DOI
    assert obj['originalId'] == '10.1234/foo'
    assert obj['collectedFromId'] == 're3data_____::r3d100010468'
    assert obj['hostedById'] == 're3data_____::r3d100010468'
    assert obj['resourceType'] == '0021'
    assert obj['type'] == 'dataset'

    minimal_oai_record.update({'resource_type': {'type': 'poster'}})
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['originalId'] == 'oai:zenodo.org:123'
    assert obj['collectedFromId'] == 'opendoar____::2659'
    assert obj['hostedById'] == 'opendoar____::2659'
    assert obj['resourceType'] == '0004'
    assert obj['type'] == 'publication'


def test_grants(app, db, minimal_oai_record, recid_pid):
    """"Test grants."""
    minimal_oai_record['grants'] = [
        {
            'acronym': 'WorkAble',
            'identifiers': {
                'eurepo': 'info:eu-repo/grantAgreement/EC/FP7/244909/'
            },
        }
    ]

    minimal_oai_record.update({'resource_type': {'type': 'dataset'}})
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['linksToProjects'] == [
        'info:eu-repo/grantAgreement/EC/FP7/244909///WorkAble'
    ]


def test_pids(app, db, minimal_oai_record, recid_pid):
    """"Test PIDs."""
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['pids'] == \
        [{'value': 'oai:zenodo.org:123', 'type': 'oai'}]

    minimal_oai_record['doi'] = '10.1234/foo'
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['pids'] == \
        [{'value': 'oai:zenodo.org:123', 'type': 'oai'},
         {'value': '10.1234/foo', 'type': 'doi'}]


def test_publisher(app, db, minimal_oai_record, recid_pid):
    """Test publisher."""
    minimal_oai_record['doi'] = '10.5281/12345'
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['publisher'] == 'Zenodo'

    minimal_oai_record['part_of'] = {'publisher': 'The Good Publisher'}
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['publisher'] == 'The Good Publisher'

    minimal_oai_record['imprint'] = {'publisher': 'The Bad Publisher'}
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['publisher'] == 'The Bad Publisher'


def test_license_code(app, db, minimal_oai_record, recid_pid):
    """Test license code."""
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['licenseCode'] == 'OPEN'

    minimal_oai_record['access_right'] = 'restricted'
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['licenseCode'] == 'RESTRICTED'

    minimal_oai_record['access_right'] = 'embargoed'
    minimal_oai_record['embargo_date'] = '2017-04-22'
    obj = openaire_json_v1.transform_record(
        recid_pid, Record(minimal_oai_record))
    assert obj['licenseCode'] == 'EMBARGO'
    assert obj['embargoEndDate'] == '2017-04-22'
