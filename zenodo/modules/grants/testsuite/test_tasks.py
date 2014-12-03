# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import

import httpretty
import json
from mock import patch

from invenio.testsuite import make_test_suite, run_test_suite
from invenio.celery.testsuite.helpers import CeleryTestCase

from .fixtures import FixtureMixin


class TasksTest(CeleryTestCase, FixtureMixin):
    @property
    def config(self):
        return dict(
            # HTTPretty doesn't play well with Redis.
            # See gabrielfalcao/HTTPretty#110
            CACHE_TYPE='simple',
            GRANTS_OPENAIRE_OAIPMH_ENDPOINT='http://example.org/oai_pmh',
        )

    @httpretty.activate
    @patch('zenodo.modules.grants.tasks.add_kb_mapping')
    @patch('zenodo.modules.grants.tasks.get_kb_mappings')
    def test_harvest_openaire_grants(self, get_kb_mappings, add_kb_mapping):
        # Mock OAI-OMH response and knowledge base.
        self.get_client()
        # Empty knowledge base
        get_kb_mappings.return_value = []

        # Test harvesting task
        from zenodo.modules.grants.tasks import \
            harvest_openaire_grants

        harvest_openaire_grants()
        assert add_kb_mapping.call_count == 200

    @patch('zenodo.modules.grants.tasks.add_kb_mapping')
    @patch('zenodo.modules.grants.tasks.update_kb_mapping')
    @patch('zenodo.modules.grants.tasks.get_kb_mappings')
    def test_task(self, get_kb_mappings, update_kb_mapping, add_kb_mapping):
        from zenodo.modules.grants.tasks import update_kb

        # Test data
        data = [
            dict(k='a', v='v1'),
            dict(k='b', v='v2'),
            dict(k='c', v='v3'),
        ]

        existing_mapping = [
            dict(key='a', value=json.dumps(data[0])),
            dict(key='b', value=json.dumps(dict(k='b', v='v4'))),
        ]

        # Mock functions
        def add_check_value(kb_name, k, v):
            assert k == 'c'
            assert v == json.dumps(data[2])

        def update_check_value(kb_name, k_old, k, v):
            assert k_old == 'b'
            assert k == 'b'
            assert v == json.dumps(data[1])

        add_kb_mapping.side_effect = add_check_value
        update_kb_mapping.side_effect = update_check_value
        get_kb_mappings.return_value = existing_mapping

        # Run update function
        update_kb('test', data, key_fun=lambda x: x['k'])
        assert add_kb_mapping.called
        assert not update_kb_mapping.called

        update_kb('test', data, key_fun=lambda x: x['k'], update=True)
        assert update_kb_mapping.called


TEST_SUITE = make_test_suite(TasksTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
