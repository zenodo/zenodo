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
from flask import current_app
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_stats import current_stats

from zenodo.modules.stats.exporters import PiwikExporter


@shared_task(ignore_result=True)
def update_record_statistics(start_date=None, end_date=None):
    """Update "_stats" field of affected records."""
    start_date = dateutil_parse(start_date) if start_date else None
    end_date = dateutil_parse(end_date) if start_date else None
    aggr_configs = {}

    if not start_date and not end_date:
        start_date = datetime.utcnow()
        end_date = datetime.utcnow()

        for aggr_name, aggr_cfg in current_stats.aggregations.items():
            aggr = aggr_cfg.cls(name=aggr_cfg.name, **aggr_cfg.params)
            if not Index(aggr.index, using=aggr.client).exists():
                if not Index(aggr.event_index, using=aggr.client).exists():
                    start_date = min(start_date, datetime.utcnow())
                else:
                    start_date = min(
                        start_date, aggr._get_oldest_event_timestamp())

            # Retrieve the last two bookmarks
            bookmarks = aggr.list_bookmarks(limit=2)
            if len(bookmarks) >= 1:
                end_date = max(
                    end_date,
                    datetime.strptime(bookmarks[0].date, aggr.doc_id_suffix))
            if len(bookmarks) == 2:
                start_date = min(
                    start_date,
                    datetime.strptime(bookmarks[1].date, aggr.doc_id_suffix))

            aggr_configs[aggr.index] = aggr
    elif start_date and end_date:
        for aggr_name, aggr_cfg in current_stats.aggregations.items():
            aggr = aggr_cfg.cls(name=aggr_cfg.name, **aggr_cfg.params)
            aggr_configs[aggr.index] = aggr
    else:
        return

    # Get conceptrecids for all the affected records between the two dates
    conceptrecids = set()
    for aggr_index, aggr in aggr_configs.items():
        query = Search(
            using=aggr.client,
            index=aggr.index,
            doc_type=aggr.doc_type,
        ).filter(
            'range', timestamp={
                'gte': start_date.replace(microsecond=0).isoformat() + '||/d',
                'lte': end_date.replace(microsecond=0).isoformat() + '||/d'}
        ).extra(_source=False)
        query.aggs.bucket('ids', 'terms', field='conceptrecid')
        conceptrecids |= {
            b.key for b in query.execute().aggregations.ids.buckets}

    indexer = RecordIndexer()
    for concpetrecid_val in conceptrecids:
        conceptrecid = PersistentIdentifier.get('recid', concpetrecid_val)
        pv = PIDVersioning(parent=conceptrecid)
        children_recids = pv.children.all()
        indexer.bulk_index([str(p.object_uuid) for p in children_recids])


@shared_task(ignore_result=True, max_retries=3, default_retry_delay=60 * 60)
def export_stats(start_date=None, end_date=None, update_bookmark=True, retry=False):
    """Export stats events."""
    if current_app.config['ZENODO_STATS_PIWIK_EXPORT_ENABLED'] is True:
        start_date = dateutil_parse(start_date) if start_date else None
        end_date = dateutil_parse(end_date) if end_date else None

        try:
            PiwikExporter().run(start_date=start_date, end_date=end_date,
                                update_bookmark=update_bookmark)
        except Exception as exc:
            if retry:
                export_stats.retry(exc=exc)
