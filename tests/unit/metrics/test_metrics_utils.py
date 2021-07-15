# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017-2021 CERN.
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

"""Test Zenodo metrics utils."""
from zenodo.modules.metrics.utils import calculate_metrics, formatted_response


def test_calculate_metrics(app, db, es, cache, use_metrics_config):
    expected_data = [
        {
            'name': 'zenodo_unique_visitors_web_total',
            'help': 'Number of unique visitors in total on Zenodo portal',
            'type': 'gauge',
            'value': 0
        },
        {
            'name': 'zenodo_researchers_total',
            'help': 'Number of researchers registered on Zenodo',
            'type': 'gauge',
            'value': 0
        },
        {
            'name': 'zenodo_files_total',
            'help': 'Number of files hosted on Zenodo',
            'type': 'gauge',
            'value': 0
        },
        {
            'name': 'zenodo_communities_total',
            'help': 'Number of Zenodo communities created',
            'type': 'gauge',
            'value': 0
        },
    ]

    calculated_metrics = calculate_metrics('openaire-nexus', cache=False)
    assert calculated_metrics == expected_data

    calculated_metrics = calculate_metrics('openaire-nexus', cache=True)
    assert calculated_metrics == expected_data


def test_formatted_response(app, use_metrics_config):
    metrics = [
        {
            'name': 'zenodo_unique_visitors_web_total',
            'help': 'Number of unique visitors in total on Zenodo portal',
            'type': 'gauge',
            'value': 0
        }
    ]

    expected_response = '# HELP zenodo_unique_visitors_web_total Number ' \
                        'of unique visitors in total on Zenodo portal\n' \
                        '# TYPE zenodo_unique_visitors_web_total gauge\n' \
                        'zenodo_unique_visitors_web_total 0\n'

    calculated_response = formatted_response(metrics)

    assert calculated_response == expected_response
