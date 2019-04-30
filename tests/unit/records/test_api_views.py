# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

"""Unit tests Zenodo JSON deserializer."""

import pytest
from flask import url_for
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search


@pytest.mark.parametrize(('val', 'status', 'error_message'), [
    ('2.45,1.63,-1.43,-1.53', 200, None),
    ('1.53  ,    -1.43  ,   2.34,1.23', 200, None),
    ('2.45,1.63', 400,
     'Invalid bounds: four comma-separated numbers required. '
     'Example: 143.37158,-38.99357,146.90918,-37.35269'),
    ('2.45,\'1.63\',-1.43,-1.53', 400, 'Invalid number in bounds.'),
    ('2.45,\' \',-1.43,-1.53', 400, 'Invalid number in bounds.'),
    ('2.45,\'\',-1.43,-1.53', 400, 'Invalid number in bounds.'),
    ('2.45,,-1.43,-1.53', 400, 'Invalid number in bounds.'),
    ('2.45, ,-1.43,-1.53', 400, 'Invalid number in bounds.'),
    ('2.45;1.63,-1.43,-1.53', 400,
     'Invalid bounds: four comma-separated numbers required. '
     'Example: 143.37158,-38.99357,146.90918,-37.35269'),
    ('181,1.63,-181,-1.53', 400, 'Longitude must be between -180 and 180.'),
    ('2.45,91,-1.43,-91', 400, 'Latitude must be between -90 and 90.'),
    ('2.45,1.63,NaN,-1.53', 400,
     'Invalid number: "NaN" is not a permitted value.'),
    ('2.45,1.63,Infinity,-1.53', 400,
     'Longitude must be between -180 and 180.'),
])
def test_geographical_search_validation(
        es, api, json_headers, record_with_bucket, val, status, error_message):
    """Test geographical search validation."""
    pid, record = record_with_bucket
    RecordIndexer().index(record)
    with api.test_request_context():
        with api.test_client() as client:
            res = client.get(
                url_for('invenio_records_rest.recid_list', locations=val),
                headers=json_headers
            )
            assert res.status_code == status
            if error_message:
                assert res.json['message'] == 'Validation error.'
                assert len(res.json['errors']) == 1
                assert res.json['errors'][0]['field'] == 'locations'
                assert res.json['errors'][0]['message'] == error_message


def test_geographical_search(es, api, json_headers, record_with_bucket):
    """Test geographical search."""
    pid, record = record_with_bucket
    record['locations'] = [
        {'lat': 46.204391, 'lon': 6.143158, 'place': 'Geneva'}]
    RecordIndexer().index(record)
    current_search.flush_and_refresh(index='records')

    with api.test_request_context():
        with api.test_client() as client:
            res = client.get(
                url_for('invenio_records_rest.recid_list',
                        locations='6.059634,46.167928,6.230161,46.244911'),
                headers=json_headers
            )
            assert len(res.json) == 1


@pytest.mark.parametrize(('val', 'status', 'error_message'), [
    ('custom-metadata-comm[dwc:family]:Felidae', 200, None),
    ('[dwc:family]:Felidae', 200, None),
    ('[dwc:foobar]:Felidae', 400, 'The "dwc:foobar" term is not supported.'),
    ('custom-metadata-comm[dwc:family]', 400, 'The parameter should have the '
     'format: custom=community[field_name]:filed_value.'),
    ('zenodo[dwc:family]:Felidae', 400,
     'The "zenodo" community does not support custom metadata.'),
    ('custom-metadata-comm[foo:bar]:Felidae', 400, 'The "foo:bar" term is not '
     'supported by the "custom-metadata-comm" community.'),
])
def test_custom_search_validation(es, api, json_headers, record_with_bucket,
                                  val, status, error_message):
    """Test custom metadata search validation."""
    pid, record = record_with_bucket
    RecordIndexer().index(record)
    with api.test_request_context():
        with api.test_client() as client:
            res = client.get(
                url_for('invenio_records_rest.recid_list', custom=val),
                headers=json_headers
            )
            assert res.status_code == status
            if error_message:
                assert res.json['message'] == 'Validation error.'
                assert len(res.json['errors']) == 1
                assert res.json['errors'][0]['field'] == 'custom'
                assert res.json['errors'][0]['message'] == error_message


def test_custom_search(es, api, json_headers, record_with_bucket,
                       custom_metadata):
    """Test custom metadata search."""
    pid, record = record_with_bucket
    record['communities'].append('custom-metadata-comm')
    record['custom'] = {'custom-metadata-comm': {'dwc:family': 'Felidae'}}
    RecordIndexer().index(record)
    current_search.flush_and_refresh(index='records')
    with api.test_request_context():
        with api.test_client() as client:
            match_queries = [
                'custom-metadata-comm[dwc:family]:Felidae',
                '[dwc:family]:Felidae',
            ]
            for q in match_queries:
                res = client.get(
                    url_for('invenio_records_rest.recid_list', custom=q),
                    headers=json_headers)
                assert len(res.json) == 1
            res = client.get(
                url_for(
                    'invenio_records_rest.recid_list',
                    custom='custom-metadata-comm[dwc:family]:foobar'),
                headers=json_headers)
            assert len(res.json) == 0
