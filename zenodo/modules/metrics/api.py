# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016-2021 CERN.
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

"""Zenodo Metrics API."""

from __future__ import absolute_import

import calendar
from datetime import datetime, timedelta

import requests
from elasticsearch_dsl import Search
from flask import current_app
from invenio_accounts.models import User
from invenio_communities.models import Community
from invenio_files_rest.models import FileInstance
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from .proxies import current_metrics


class ZenodoMetric(object):
    """API class for Zenodo Metrics."""

    @staticmethod
    def get_data_transfer():
        """Get file transfer volume in TB."""
        time_range = {'gte': current_metrics.metrics_start_date.isoformat()}

        search = Search(
            using=current_search_client,
            index=build_alias_name('stats-file-download-*')
        ).filter(
            'range', timestamp=time_range,
        ).filter(
            'term', is_parent=False,
        ).params(request_timeout=120)
        search.aggs.metric('download_volume', 'sum', field='volume')
        result = search[:0].execute().aggregations.to_dict()
        download_volume = result.get('download_volume', {}).get('value', 0)

        search = Search(
            using=current_search_client,
            index=build_alias_name('records')
        ).filter('range', created=time_range).params(request_timeout=120)
        search.aggs.metric('upload_volume', 'sum', field='size')
        result = search[:0].execute().aggregations.to_dict()
        upload_volume = result.get('upload_volume', {}).get('value', 0)

        return int(download_volume + upload_volume)

    @staticmethod
    def get_visitors():
        """Get number of unique zenodo users."""
        time_range = {'gte': current_metrics.metrics_start_date.isoformat()}

        search = Search(
            using=current_search_client,
            index=build_alias_name('events-stats-*')
        ).filter('range', timestamp=time_range).params(request_timeout=120)

        search.aggs.metric(
            'visitors_count', 'cardinality', field='visitor_id'
        )
        result = search[:0].execute()

        if 'visitors_count' not in result.aggregations:
            return 0

        return int(result.aggregations.visitors_count.value)

    @staticmethod
    def get_uptime():
        """Get Zenodo uptime."""
        metrics = current_app.config['ZENODO_METRICS_UPTIME_ROBOT_METRIC_IDS']
        url = current_app.config['ZENODO_METRICS_UPTIME_ROBOT_URL']
        api_key = current_app.config['ZENODO_METRICS_UPTIME_ROBOT_API_KEY']

        end = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (end - timedelta(days=1)).replace(day=1)
        end_ts = calendar.timegm(end.utctimetuple())
        start_ts = calendar.timegm(start.utctimetuple())

        res = requests.post(url, json={
            'api_key': api_key,
            'custom_uptime_ranges': '{}_{}'.format(start_ts, end_ts),
        })

        return sum(
            float(d['custom_uptime_ranges'])
            for d in res.json()['monitors']
            if d['id'] in metrics
        ) / len(metrics)

    @staticmethod
    def get_researchers():
        """Get number of unique zenodo users."""
        return User.query.filter(
            User.confirmed_at.isnot(None),
            User.active.is_(True),
        ).count()

    @staticmethod
    def get_files():
        """Get number of files."""
        return FileInstance.query.count()

    @staticmethod
    def get_communities():
        """Get number of active communities."""
        return Community.query.filter(
            Community.deleted_at.is_(None)
        ).count()
