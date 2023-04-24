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

"""Configuration for Zenodo Metrics."""

from __future__ import absolute_import, print_function

import datetime

from .api import ZenodoMetric

ZENODO_METRICS_START_DATE = datetime.datetime(2021, 1, 1)
ZENODO_METRICS_CACHE_TIMEOUT = int(datetime.timedelta(hours=1).total_seconds())
ZENODO_METRICS_CACHE_UPDATE_INTERVAL = datetime.timedelta(minutes=30)

ZENODO_METRICS_UPTIME_ROBOT_METRIC_IDS = {}
ZENODO_METRICS_UPTIME_ROBOT_URL = 'https://api.uptimerobot.com/v2/getMonitors'
ZENODO_METRICS_UPTIME_ROBOT_API_KEY = None

ZENODO_METRICS_DATA = {
    'openaire-nexus': [
        {
            'name': 'zenodo_nexus_data_transfer_bytes_total',
            'help': (
                'Bytes of data transferred from/to Zenodo during the '
                'OpenAIRE-NEXUS project (i.e. from 2021-01-01).'
            ),
            'type': 'counter',
            'value': ZenodoMetric.get_data_transfer
        },
        {
            'name': 'zenodo_nexus_unique_visitors_web_total',
            'help': (
                'Total of daily unique visitors on Zenodo portal during the '
                'OpenAIRE-NEXUS project (i.e. from 2021-01-01).'
            ),
            'type': 'counter',
            'value': ZenodoMetric.get_visitors
        },
        {
            'name': 'zenodo_last_month_uptime_ratio',
            'help': 'Zenodo uptime percentage for the last month.',
            'type': 'gauge',
            'value': ZenodoMetric.get_uptime
        },
        {
            'name': 'zenodo_researchers',
            'help': 'Number of researchers registered on Zenodo',
            'type': 'gauge',
            'value': ZenodoMetric.get_researchers
        },
        {
            'name': 'zenodo_files',
            'help': 'Number of files hosted on Zenodo',
            'type': 'gauge',
            'value': ZenodoMetric.get_files
        },
        {
            'name': 'zenodo_communities',
            'help': 'Number of Zenodo communities created',
            'type': 'gauge',
            'value': ZenodoMetric.get_communities
        },
    ]
}
