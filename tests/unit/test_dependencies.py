# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016-2018 CERN.
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

"""Basics tests to ensure DB and Elasticsearch is running."""

from invenio_search import current_search, current_search_client


def test_es_running(app):
    """Test search view."""
    assert current_search_client.ping()


def test_es_state(app, es):
    """Test generated mappings, templates and aliases on ElasticSearch."""
    prefix = app.config['SEARCH_INDEX_PREFIX']
    suffix = current_search._current_suffix

    assert current_search_client.indices.get_alias() == {
            prefix + 'grants-grant-v1.0.0' + suffix: {
                'aliases': {
                    prefix + 'grants': {},
                    prefix + 'grants-grant-v1.0.0': {}
                }
            },
            prefix + 'records-record-v1.0.0' + suffix: {
                'aliases': {
                    prefix + 'records': {},
                    prefix + 'records-record-v1.0.0': {}
                }
            },
            prefix + 'deposits-records-record-v1.0.0' + suffix: {
                'aliases': {
                    prefix + 'deposits-records-record-v1.0.0': {},
                    prefix + 'deposits': {},
                    prefix + 'deposits-records': {}
                }
            },
            prefix + 'licenses-license-v1.0.0' + suffix: {
                'aliases': {
                    prefix + 'licenses-license-v1.0.0': {},
                    prefix + 'licenses': {}
                }
            },
            prefix + 'funders-funder-v1.0.0' + suffix: {
                'aliases': {
                    prefix + 'funders': {},
                    prefix + 'funders-funder-v1.0.0': {}
                }
            },
        }

    templates = {
        k: (set(v['index_patterns']), set(v['aliases'].keys()))
        for k, v in current_search_client.indices.get_template().items()
    }
    assert templates == {
        prefix + 'stats-templates-events/v7-record-view-v1.0.0': (
            {prefix + 'events-stats-record-view-*'},
            {prefix + 'events-stats-record-view'},
        ),
        prefix + 'stats-templates-events/v7-file-download-v1.0.0': (
            {prefix + 'events-stats-file-download-*'},
            {prefix + 'events-stats-file-download'},
        ),
        prefix + 'stats-templates-aggregations/v7-aggr-record-view-v1.0.0': (
            {prefix + 'stats-record-view-*'},
            {prefix + 'stats-record-view'},
        ),
        prefix + 'stats-templates-aggregations/v7-aggr-record-download-v1.0.0':
            (
            {prefix + 'stats-file-download-*'},
            {prefix + 'stats-file-download'},
        ),
    }
