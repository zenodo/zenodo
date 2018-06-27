# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Registration of aggregations."""

from invenio_search import current_search_client
from invenio_stats.aggregations import StatAggregator


def register_aggregations():
    """Register Zenodo aggregations."""
    return [dict(
        aggregation_name='record-download-agg',
        templates='zenodo.modules.stats.templates.aggregations',
        aggregator_class=StatAggregator,
        aggregator_config=dict(
            client=current_search_client,
            event='file-download',
            aggregation_field='recid',
            aggregation_interval='day',
            copy_fields=dict(
                bucket_id='bucket_id',
                record_id='record_id',
                recid='recid',
                conceptrecid='conceptrecid',
                doi='doi',
                conceptdoi='conceptdoi',
                communities=lambda d, _: (list(d.communities)
                                          if d.communities else None),
                is_parent=lambda *_: False
            ),
            metric_aggregation_fields=dict(
                unique_count=('cardinality', 'unique_session_id'),
                volume=('sum', 'size'),
            )
        )),
        dict(
            aggregation_name='record-download-all-versions-agg',
            templates='zenodo.modules.stats.templates.aggregations',
            aggregator_class=StatAggregator,
            aggregator_config=dict(
                client=current_search_client,
                event='file-download',
                aggregation_field='conceptrecid',
                aggregation_interval='day',
                copy_fields=dict(
                    conceptrecid='conceptrecid',
                    conceptdoi='conceptdoi',
                    communities=lambda d, _: (list(d.communities)
                                              if d.communities else None),
                    is_parent=lambda *_: True
                ),
                metric_aggregation_fields=dict(
                    unique_count=('cardinality', 'unique_session_id'),
                    volume=('sum', 'size'),
                )
            )),
        dict(
            aggregation_name='record-view-agg',
            templates='zenodo.modules.stats.templates.aggregations',
            aggregator_class=StatAggregator,
            aggregator_config=dict(
                client=current_search_client,
                event='record-view',
                aggregation_field='recid',
                aggregation_interval='day',
                copy_fields=dict(
                    record_id='record_id',
                    recid='recid',
                    conceptrecid='conceptrecid',
                    doi='doi',
                    conceptdoi='conceptdoi',
                    communities=lambda d, _: (list(d.communities)
                                              if d.communities else None),
                    is_parent=lambda *_: False
                ),
                metric_aggregation_fields=dict(
                    unique_count=('cardinality', 'unique_session_id'),
                )
            )),
        dict(
            aggregation_name='record-view-all-versions-agg',
            templates='zenodo.modules.stats.templates.aggregations',
            aggregator_class=StatAggregator,
            aggregator_config=dict(
                client=current_search_client,
                event='record-view',
                aggregation_field='conceptrecid',
                aggregation_interval='day',
                copy_fields=dict(
                    conceptrecid='conceptrecid',
                    conceptdoi='conceptdoi',
                    communities=lambda d, _: (list(d.communities)
                                              if d.communities else None),
                    is_parent=lambda *_: True
                ),
                metric_aggregation_fields=dict(
                    unique_count=('cardinality', 'unique_session_id'),
                )
            )),

    ]
