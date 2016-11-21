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

"""Test for Zenodo Auditor OAI-PMH checks."""

from __future__ import absolute_import, print_function

import logging

import pytest
from invenio_communities.models import Community
from invenio_indexer.api import RecordIndexer
from invenio_oaiserver.models import OAISet
from invenio_search import current_search
from mock import MagicMock, patch

from zenodo.modules.auditor.oai import OAIAudit, OAICorrespondenceCheck, \
    OAISetResultCheck

oai_set_result_count_params = (
    ([], [], [], []),
    (['a', 'b'], ['user-a', 'user-b'], [], []),
    (['a'], [], ['a'], []),
    ([], ['user-a'], [], ['user-a']),
    (['a'], ['user-b'], ['a'], ['user-b']),
)


@pytest.mark.parametrize(
    ('oai_communities', 'oai_sets', 'missing_oai_set', 'missing_community'),
    oai_set_result_count_params
)
def test_oai_set_correspondence(db, users, oai_communities, oai_sets,
                                missing_oai_set, missing_community):
    for c in oai_communities:
        with db.session.begin_nested():
            new_comm = Community.create(community_id=c, user_id=1)
        db.session.commit()

        # Delete the automatically created OAI Set id required by test case
        if new_comm.oaiset_spec not in oai_sets:
            with db.session.begin_nested():
                db.session.delete(new_comm.oaiset)
            db.session.commit()

    for s in oai_sets:
        if not OAISet.query.filter_by(spec=s).one_or_none():
            with db.session.begin_nested():
                db.session.add(OAISet(spec=s))
            db.session.commit()
    check = OAICorrespondenceCheck()
    check.perform()

    assert set(check.issues.get('missing_oai_set', [])) == set(missing_oai_set)
    assert set(check.issues.get('missing_community', [])) == \
        set(missing_community)


oai_set_result_count_params = (
    (
        # (State for DB, ES, /oai2d) and...
        ([], [], []),
        # (Issues for DB, ES, /oai2d)
        ([], [], [])
    ),

    (([], [], [1]),
     ([1], [1], [])),

    (([], [1], []),
     ([1], [], [1])),

    (([], [1], [1]),
     ([1], [], [])),

    (([1], [], []),
     ([], [1], [1])),

    (([1], [], [1]),
     ([], [1], [])),

    (([1], [1], []),
     ([], [], [1])),

    (([1], [1], [1]),
     ([], [], [])),

    (([1], [2], [3]),
     ([2, 3], [1, 3], [1, 2])),

    (([1, 4], [2, 4], [3, 4]),
     ([2, 3], [1, 3], [1, 2])),
)


@pytest.mark.parametrize(('oai_sources', 'issues'),
                         oai_set_result_count_params)
def test_oai_set_result_count(audit_records, db, es, communities, oai_sources,
                              issues):
    db_records, es_records, oai2d_records = oai_sources

    for recid in db_records:
        record = audit_records[recid]
        record['_oai']['sets'] = ['user-c1']
        record.commit()
    db.session.commit()

    indexer = RecordIndexer()
    for recid in es_records:
        record = audit_records[recid]
        record['_oai']['sets'] = ['user-c1']
        indexer.index(record)
    current_search.flush_and_refresh(index='records')

    # '/oai2d' needs straight-forward cheating... There's no way to be sure
    # why the endpoint sometimes fails to report the correct results. It could
    # be a Resumption Token issue, or even an indexing issue on Elasticsearch.
    # Either way, we have to be able to replicate when running on production
    # this behavior and report it as an issue.
    oai2d_ids_mock = MagicMock()
    oai2d_ids_mock.return_value = set(oai2d_records)
    with patch('zenodo.modules.auditor.oai.OAISetResultCheck'
               '._oai2d_endpoint_identifiers', new=oai2d_ids_mock):
        audit = OAIAudit('testAudit', logging.getLogger('auditorTesting'), [])
        check = OAISetResultCheck(audit, Community.get('c1'))
        check.perform()
        audit.clear_db_oai_set_cache()

        result_issues = check.issues.get('missing_ids', {})
        db_issues, es_issues, api_issues = issues
        assert set(result_issues.get('db', [])) == set(db_issues)
        assert set(result_issues.get('es', [])) == set(es_issues)
        assert set(result_issues.get('api', [])) == set(api_issues)
