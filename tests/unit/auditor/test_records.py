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

"""Test for Zenodo Auditor Record checks."""

from __future__ import absolute_import, print_function

import logging

import pytest
from invenio_records.models import RecordMetadata

from zenodo.modules.auditor.records import RecordAudit, RecordCheck
from zenodo.modules.records.api import ZenodoRecord


@pytest.fixture()
def record_audit():
    return RecordAudit('testAudit', logging.getLogger('auditorTesting'), [])


def test_record_audit(record_audit, full_record, db, communities, users,
                      oaiid_pid):
    # Add the "ecfunded" community since it's usually being added automatically
    # after processing a deposit if the record has an EC grant.
    oaiid_pid.pid_value = full_record['communities'].append('ecfunded')

    # Mint the OAI identifier
    oaiid_pid.pid_value = full_record['_oai']['id']
    db.session.add(oaiid_pid)

    # Create the record metadata, to store the
    record_model = RecordMetadata()
    record_model.json = full_record
    db.session.add(record_model)

    db.session.commit()

    record = ZenodoRecord(data=full_record, model=record_model)
    check = RecordCheck(record_audit, record)
    check.perform()

    assert check.issues == {}
    assert check.is_ok is True
    assert check.dump() == {
        'record': {
            'recid': record['recid'],
            'object_uuid': str(record.id),
        },
        'issues': {},
    }


duplicate_community_params = (
    ([], None),
    (['a', 'b'], None),
    (['a', 'a', 'a', 'b'], ['a']),
    (['a', 'a', 'b', 'b'], ['a', 'b']),
)


@pytest.mark.parametrize(('record_communities', 'issue'),
                         duplicate_community_params)
def test_duplicate_communities(record_audit, minimal_record,
                               record_communities, issue):
    minimal_record.update({'communities': record_communities})
    check = RecordCheck(record_audit, minimal_record)
    check._duplicate_communities()

    result_issue = check.issues.get('communities', {}).get('duplicates')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


unresolvable_communities_params = (
    ([], None),
    (['c1', 'c2', 'c3', 'c4', 'zenodo', 'ecfunded'], None),
    (['foo'], ['foo']),
    (['c1', 'c2', 'foo'], ['foo']),
    (['foo', 'bar'], ['foo', 'bar']),
)


@pytest.mark.parametrize(('record_communities', 'issue'),
                         unresolvable_communities_params)
def test_unresolvable_communities(record_audit, minimal_record, communities,
                                  record_communities, issue):
    minimal_record.update({'communities': record_communities})
    check = RecordCheck(record_audit, minimal_record)
    check._unresolvable_communities()

    result_issue = check.issues.get('communities', {}).get('unresolvable')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


duplicate_owners_params = (
    ([1], None),
    ([1, 2, 3], None),
    ([1, 1, 1, 2], [1]),
    ([1, 1, 2, 2], [1, 2]),
)


@pytest.mark.parametrize(('record_owners', 'issue'), duplicate_owners_params)
def test_duplicate_owners(record_audit, minimal_record, record_owners, issue):
    minimal_record.update({'owners': record_owners})
    check = RecordCheck(record_audit, minimal_record)
    check._duplicate_owners()

    result_issue = check.issues.get('owners', {}).get('duplicates')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


unresolvable_owners_params = (
    ([1], None),
    ([1, 2, 3], None),
    ([4], [4]),
    ([1, 2, 3, 4], [4]),
)


@pytest.mark.parametrize(('record_owners', 'issue'),
                         unresolvable_owners_params)
def test_unresolvable_owners(record_audit, minimal_record, users,
                             record_owners, issue):
    minimal_record.update({'owners': record_owners})
    check = RecordCheck(record_audit, minimal_record)
    check._unresolvable_owners()

    result_issue = check.issues.get('owners', {}).get('unresolvable')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


duplicate_grants_params = (
    ([], None),
    ([{'$ref': '1'}, {'$ref': '2'}], None),
    ([{'$ref': '1'}, {'$ref': '1'}], ['1']),
    ([{'$ref': '1'}, {'$ref': '1'}, {'$ref': '2'}], ['1']),
    ([{'$ref': '1'}, {'$ref': '1'}, {'$ref': '2'}, {'$ref': '2'}], ['1', '2']),
)


@pytest.mark.parametrize(('record_grants', 'issue'), duplicate_grants_params)
def test_duplicate_grants(record_audit, minimal_record, record_grants, issue):
    minimal_record.update({'grants': record_grants})
    check = RecordCheck(record_audit, minimal_record)
    check._duplicate_grants()

    result_issue = check.issues.get('grants', {}).get('duplicates')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


duplicate_files_params = [
    ([{'key': 'a', 'version_id': 1}], None),

    ([{'key': 'a', 'version_id': 1},
      {'key': 'b', 'version_id': 2},
      {'key': 'c', 'version_id': 3}],
     None),

    ([{'key': 'a', 'version_id': 1},
      {'key': 'a', 'version_id': 2},
      {'key': 'a', 'version_id': 3},
      {'key': 'b', 'version_id': 4}],
     [{'key': 'a', 'version_id': 1},
      {'key': 'a', 'version_id': 2},
      {'key': 'a', 'version_id': 3}]),

    ([{'key': 'a', 'version_id': 1},
      {'key': 'b', 'version_id': 1},
      {'key': 'c', 'version_id': 1},
      {'key': 'd', 'version_id': 2}],
     [{'key': 'a', 'version_id': 1},
      {'key': 'b', 'version_id': 1},
      {'key': 'c', 'version_id': 1}]),
]


@pytest.mark.parametrize(('record_files', 'issue'), duplicate_files_params)
def test_duplicate_files(record_audit, minimal_record, record_files, issue):
    minimal_record.update({'_files': record_files})
    check = RecordCheck(record_audit, minimal_record)
    check._duplicate_files()

    result_issue = check.issues.get('files', {}).get('duplicates')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert result_issue == issue


missing_files_params = [
    ([{'key': 'a'}], False),
    ([{'key': 'a'}, {'key': 'b'}], False),
    (None, True),
    ([], True),
]


@pytest.mark.parametrize(('record_files', 'issue'), missing_files_params)
def test_missing_files(record_audit, minimal_record, record_files, issue):
    minimal_record.update({'_files': record_files})
    check = RecordCheck(record_audit, minimal_record)
    check._missing_files()

    result_issue = check.issues.get('files', {}).get('missing')
    assert bool(result_issue) == bool(issue)


multiple_buckets_params = [
    ([{'bucket': 'a'}], None),
    ([{'bucket': 'a'}, {'bucket': 'a'}, {'bucket': 'a'}], None),
    ([{'bucket': 'a'}, {'bucket': 'a'}, {'bucket': 'b'}], ['a', 'b']),
    ([{'bucket': 'a'}, {'bucket': 'b'}, {'bucket': 'c'}], ['a', 'b', 'c']),
]


@pytest.mark.parametrize(('record_files', 'issue'), multiple_buckets_params)
def test_multiple_buckets(record_audit, minimal_record, record_files, issue):
    minimal_record.update({'_files': record_files})
    check = RecordCheck(record_audit, minimal_record)
    check._multiple_buckets()

    result_issue = check.issues.get('files', {}).get('multiple_buckets')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


bucket_mismatch_params = [
    ('a', [{'bucket': 'a'}], None),
    ('a', [{'key': 'f1', 'bucket': 'a'}, {'key': 'f2', 'bucket': 'a'}], None),
    ('a', [{'key': 'f1', 'bucket': 'b'}], [{'key': 'f1', 'bucket': 'b'}]),
    ('a', [{'key': 'f1', 'bucket': 'a'}, {'key': 'f2', 'bucket': 'b'}],
     [{'key': 'f2', 'bucket': 'b'}]),
]


@pytest.mark.parametrize(('record_bucket', 'record_files', 'issue'),
                         bucket_mismatch_params)
def test_bucket_mismatch(record_audit, minimal_record, record_bucket,
                         record_files, issue):
    minimal_record.update({'_buckets': {'record': record_bucket}})
    minimal_record.update({'_files': record_files})
    check = RecordCheck(record_audit, minimal_record)
    check._bucket_mismatch()

    result_issue = check.issues.get('files', {}).get('bucket_mismatch')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert result_issue == issue


oai_required_params = [
    ({'id': 'oai:zenodo.org:1', 'updated': '2016-01-01T12:00:00Z'}, None),
    ({}, {'id': True, 'updated': True}),
    ({'id': 'oai:zenodo.org:1'}, {'updated': True}),
    ({'updated': '2016-01-01T12:00:00Z'}, {'id': True}),
]


@pytest.mark.parametrize(('record_oai', 'issue'), oai_required_params)
def test_oai_required(record_audit, minimal_record, record_oai, issue):
    minimal_record.update({'_oai': record_oai})
    check = RecordCheck(record_audit, minimal_record)
    check._oai_required()

    result_issue = check.issues.get('oai', {}).get('missing')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert result_issue == issue


oai_non_minted_pid_params = [
    ({'id': 'oai:zenodo.org:123'}, None),
    ({'id': 'oai:zenodo.org:invalid'}, 'oai:zenodo.org:invalid'),
]


@pytest.mark.parametrize(('record_oai', 'issue'), oai_non_minted_pid_params)
def test_oai_non_minted_pid(record_audit, minimal_record, db, oaiid_pid,
                            record_oai, issue):
    db.session.add(oaiid_pid)
    db.session.commit()
    minimal_record.update({'_oai': record_oai})
    check = RecordCheck(record_audit, minimal_record)
    check._oai_non_minted_pid()

    result_issue = check.issues.get('oai', {}).get('non_minted_pid')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert result_issue == issue


oai_duplicate_sets_params = [
    ({}, None),
    ({'sets': ['a', 'b']}, None),
    ({'sets': ['a', 'a', 'a', 'b']}, ['a']),
    ({'sets': ['a', 'a', 'b', 'b']}, ['a', 'b']),
]


@pytest.mark.parametrize(('record_oai', 'issue'), oai_duplicate_sets_params)
def test_oai_duplicate_sets(record_audit, minimal_record, record_oai, issue):
    minimal_record.update({'_oai': record_oai})
    check = RecordCheck(record_audit, minimal_record)
    check._oai_duplicate_sets()

    result_issue = check.issues.get('oai', {}).get('duplicate_oai_sets')
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert len(result_issue) == len(issue)
        assert set(result_issue) == set(issue)


oai_community_correspondence = [
    ([], [], None),
    (['a'], ['user-a'], None),
    (['a', 'b'], ['user-a', 'user-b'], None),

    (['a'], [], {'missing_oai_sets': ['user-a']}),
    (['a', 'b'], ['user-a'], {'missing_oai_sets': ['user-b'], }),

    ([], ['user-a'], {'redundant_oai_sets': ['user-a']}),
    (['a'], ['user-a', 'user-b'], {'redundant_oai_sets': ['user-b']}),

    (['a'], ['user-b'],
     {'redundant_oai_sets': ['user-b'], 'missing_oai_sets': ['user-a']}),
]


@pytest.mark.parametrize(('record_communities', 'record_oai', 'issue'),
                         oai_community_correspondence)
def test_oai_community_correspondence(record_audit, minimal_record, db,
                                      record_communities, record_oai, issue):
    minimal_record.update({'communities': record_communities})
    minimal_record.update({'_oai': {'sets': record_oai}})
    check = RecordCheck(record_audit, minimal_record)
    check._oai_community_correspondence()

    result_issue = check.issues.get('oai', {})
    assert bool(result_issue) == bool(issue)
    if result_issue and issue:
        assert result_issue == issue


def test_jsonschema(app, record_audit, minimal_record):
    check = RecordCheck(record_audit, ZenodoRecord(minimal_record))
    check.jsonschema()
    assert check.issues.get('jsonschema') is None

    minimal_record['invalid_key'] = 'should not be here'
    check = RecordCheck(record_audit, ZenodoRecord(minimal_record))
    check.jsonschema()
    assert check.issues.get('jsonschema')
