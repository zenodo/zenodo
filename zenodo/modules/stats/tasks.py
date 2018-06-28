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

"""Tasks for statistics."""

from celery import shared_task
from invenio_stats import current_stats
from elasticsearch_dsl import Index, Search
import datetime
from invenio_indexer.api import RecordIndexer


@shared_task(ignore_result=True)
def update_record_statistics():
    # Get last 2 bookmarks for aggregations
    start_date = datetime.date.today()
    end_date = datetime.date.today()

    aggr_indices = set()

    for a in current_stats.enabled_aggregations:
        aggregator = current_stats.aggregations[a].aggregator_class(
            **current_stats.aggregations[a].aggregator_config)

        # Get the last two bookmarks
        if not Index(aggregator.aggregation_alias,
                     using=aggregator.client).exists():
            if not Index(aggregator.event_index,
                         using=aggregator.client).exists():
                start_date = min(start_date, datetime.date.today())
            start_date = min(start_date,
                             aggregator._get_oldest_event_timestamp())

        # Retrieve the last two bookmarks
        bookmarks = Search(
            using=aggregator.client,
            index=aggregator.aggregation_alias,
            doc_type='{0}-bookmark'.format(aggregator.event)
        )[0:2].sort({'date': {'order': 'desc'}}).execute()

        if len(bookmarks) >= 1:
            end_date = max(
                end_date, datetime.datetime.strptime(
                    bookmarks[0].date, aggregator.doc_id_suffix).date())
        if len(bookmarks) == 2:
            start_date = min(
                start_date, datetime.datetime.strptime(
                    bookmarks[1].date, aggregator.doc_id_suffix).date())

        aggr_indices.add(aggregator.aggregation_alias)

    import wdb; wdb.set_trace()

    # Get all the affected records between the two dates:
    record_ids = set()
    for i in aggr_indices:
        doc_type = '{0}-{1}-aggregation'.format(
            aggregator.event, aggregator.aggregation_interval)
        query = Search(
            using=aggregator.client,
            index=aggregator.aggregation_alias,
            doc_type=doc_type,
        ).filter(
            'range', timestamp={'gte': start_date.isoformat(),
                                'lte': end_date.isoformat()}
        ).extra(_source=False)
        query.aggs.bucket('ids', 'terms', field='record_id', size=0)
        record_ids |= {b.key for b in query.execute().aggregations.ids.buckets}

    RecordIndexer().bulk_index(record_ids)
