# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

from elasticsearch_dsl import Search
from invenio_accounts.models import User
from invenio_communities.models import Community
from invenio_files_rest.models import FileInstance
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from .proxies import current_metrics


class ZenodoMetric(object):
    """API class for Zenodo Metrics."""

    @staticmethod
    def get_users():
        """Get number of unique zenodo users."""
        return 1

    @staticmethod
    def get_visitors():
        """Get number of unique zenodo users."""
        time_range = {'gte': current_metrics.metrics_start_date.isoformat()}

        search = Search(
            using=current_search_client,
            index=build_alias_name('events-stats-*')
        ).filter('range', timestamp=time_range)

        search.aggs.metric(
            'visitors_count', 'cardinality', field='visitor_id'
        )
        result = search.execute()

        if 'visitors_count' not in result.aggregations:
            return 0

        return result.aggregations.visitors_count.value

    @staticmethod
    def get_researchers():
        """Get number of unique zenodo users."""
        return User.query.filter(
            User.confirmed_at >= current_metrics.metrics_start_date,
            User.confirmed_at.isnot(None),
            User.active.is_(True),
        ).count()

    @staticmethod
    def get_files():
        """Get number of files."""
        return FileInstance.query.filter(
            FileInstance.created >= current_metrics.metrics_start_date
        ).count()

    @staticmethod
    def get_communities():
        """Get number of active communities."""
        return Community.query.filter(
            Community.created >= current_metrics.metrics_start_date,
            Community.deleted_at.is_(None)
        ).count()
