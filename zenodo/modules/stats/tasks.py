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

from datetime import datetime

from celery import shared_task
from dateutil.parser import parse as dateutil_parse
from elasticsearch_dsl import Index, Search
from invenio_indexer.api import RecordIndexer
from invenio_stats import current_stats


@shared_task(ignore_result=True)
def update_record_statistics(start_date=None, end_date=None):
    """Update "_stats" field of affected records."""
    aggr_configs = {}

    if not start_date and not end_date:
        start_date = datetime.utcnow()
        end_date = datetime.utcnow()

        for aggr_name in current_stats.enabled_aggregations:
            aggr_cfg = current_stats.aggregations[aggr_name]
            aggr = aggr_cfg.aggregator_class(
                name=aggr_cfg.name, **aggr_cfg.aggregator_config)

            if not Index(aggr.aggregation_alias, using=aggr.client).exists():
                if not Index(aggr.event_index, using=aggr.client).exists():
                    start_date = min(start_date, datetime.utcnow())
                else:
                    start_date = min(
                        start_date, aggr._get_oldest_event_timestamp())

            # Retrieve the last two bookmarks
            bookmarks = Search(
                using=aggr.client,
                index=aggr.aggregation_alias,
                doc_type=aggr.bookmark_doc_type
            )[0:2].sort({'date': {'order': 'desc'}}).execute()

            if len(bookmarks) >= 1:
                end_date = max(
                    end_date,
                    datetime.strptime(bookmarks[0].date, aggr.doc_id_suffix))
            if len(bookmarks) == 2:
                start_date = min(
                    start_date,
                    datetime.strptime(bookmarks[1].date, aggr.doc_id_suffix))

            aggr_configs[aggr.aggregation_alias] = aggr
    elif start_date and end_date:
        start_date = dateutil_parse(start_date)
        end_date = dateutil_parse(end_date)

        for aggr_name in current_stats.enabled_aggregations:
            aggr_cfg = current_stats.aggregations[aggr_name]
            aggr = aggr_cfg.aggregator_class(
                name=aggr_cfg.name, **aggr_cfg.aggregator_config)
            aggr_configs[aggr.aggregation_alias] = aggr
    else:
        return

    # Get all the affected records between the two dates:
    record_ids = set()
    for aggr_alias, aggr in aggr_configs.items():
        query = Search(
            using=aggr.client,
            index=aggr.aggregation_alias,
            doc_type=aggr.aggregation_doc_type,
        ).filter(
            'range', timestamp={
                'gte': start_date.replace(microsecond=0).isoformat() + '||/d',
                'lte': end_date.replace(microsecond=0).isoformat() + '||/d'}
        ).extra(_source=False)
        query.aggs.bucket('ids', 'terms', field='record_id', size=0)
        record_ids |= {b.key for b in query.execute().aggregations.ids.buckets}

    RecordIndexer().bulk_index(record_ids)
