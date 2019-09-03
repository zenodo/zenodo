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

from invenio_search import current_search_client


def test_es_running(app):
    """Test search view."""
    assert current_search_client.ping()


def test_es_state(app, es):
    """Test generated mappings, templates and aliases on ElasticSearch."""
    assert current_search_client.indices.get_aliases() == {
        'deposits-deposit-v1.0.0': {  # leftover from invenio-deposit
            'aliases': {'deposits': {}}},
        'deposits-records-record-v1.0.0': {
            'aliases': {'deposits': {}, 'deposits-records': {}}},
        'funders-funder-v1.0.0': {
            'aliases': {'funders': {}}},
        'grants-grant-v1.0.0': {
            'aliases': {'grants': {}}},
        'licenses-license-v1.0.0': {
            'aliases': {'licenses': {}}},
        'records-record-v1.0.0': {
            'aliases': {'records': {}}},
    }
    templates = {
        k: (v['template'], set(v['aliases'].keys()), set(v['mappings'].keys()))
        for k, v in current_search_client.indices.get_template().items()
    }
    assert templates == {
        'stats-templates-events/v2-record-view-v1.0.0': (
            'events-stats-record-view-*',
            {'events-stats-record-view'},
            {'stats-record-view'},
        ),
        'stats-templates-events/v2-file-download-v1.0.0': (
            'events-stats-file-download-*',
            {'events-stats-file-download'},
            {'_default_', 'stats-file-download'},
        ),
        'stats-templates-aggregations/v2-aggr-record-view-v1.0.0': (
            'stats-record-view-*',
            {'stats-record-view'},
            {
                'record-view-day-aggregation',
                'record-view-agg-bookmark',
                'record-view-all-versions-agg-bookmark',
            },

        ),
        'stats-templates-aggregations/v2-aggr-record-download-v1.0.0': (
            'stats-file-download-*',
            {'stats-file-download'},
            {
                '_default_',
                'file-download-day-aggregation',
                'record-download-agg-bookmark',
                'record-download-all-versions-agg-bookmark',
            },
        ),
    }
