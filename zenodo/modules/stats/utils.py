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

"""Statistics utilities."""

import itertools
import math

from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search
from flask import request
from flask.globals import current_app
from invenio_pidstore.models import PersistentIdentifier
from invenio_search.proxies import current_search_client
from invenio_search.utils import build_alias_name
from invenio_stats import current_stats

from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.resolvers import record_resolver

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


def get_record_from_context(**kwargs):
    """Get the cached record object from kwargs or the request context."""
    if 'record' in kwargs:
        return kwargs['record']
    else:
        if request and \
                hasattr(request._get_current_object(), 'current_file_record'):
            return request.current_file_record


def extract_event_record_metadata(record):
    """Extract from a record the payload needed for a statistics event."""
    return dict(
        record_id=str(record.id),
        recid=str(record['recid']) if record.get('recid') else None,
        conceptrecid=record.get('conceptrecid'),
        doi=record.get('doi'),
        conceptdoi=record.get('conceptdoi'),
        access_right=record.get('access_right'),
        resource_type=record.get('resource_type'),
        communities=record.get('communities'),
        owners=record.get('owners'),
        revision_id=record.get('revision_id'),
        publication_date=record.get('publication_date')
    )


def build_record_stats(recid, conceptrecid):
    """Build the record's stats."""
    stats = {}
    stats_sources = {
        'record-view': {
            'params': {'recid': recid},
            'fields': {
                'views': 'count',
                'unique_views': 'unique_count',
            },
        },
        'record-download': {
            'params': {'recid': recid},
            'fields': {
                'downloads': 'count',
                'unique_downloads': 'unique_count',
                'volume': 'volume',
            },
        },
        'record-view-all-versions': {
            'params': {'conceptrecid': conceptrecid},
            'fields': {
                'version_views': 'count',
                'version_unique_views': 'unique_count',
            }
        },
        'record-download-all-versions': {
            'params': {'conceptrecid': conceptrecid},
            'fields': {
                'version_downloads': 'count',
                'version_unique_downloads': 'unique_count',
                'version_volume': 'volume',
            },
        },
    }
    for query_name, cfg in stats_sources.items():
        try:
            query_cfg = current_stats.queries[query_name]
            query = query_cfg.cls(name=query_name, **query_cfg.params)
            result = query.run(**cfg['params'])
            for dst, src in cfg['fields'].items():
                stats[dst] = result.get(src)
        except Exception:
            pass
    return stats


def get_record_stats(recordid, throws=True):
    """Fetch record statistics from Elasticsearch."""
    try:
        res = current_search_client.get(
            index=build_alias_name('records'),
            id=recordid,
            params={'_source_includes': '_stats'},
        )
        return res['_source']['_stats']
    except NotFoundError:
        return None
    except Exception:
        if throws:
            raise
        pass


def chunkify(iterable, n):
    """Create equally sized tuple-chunks from an iterable."""
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


@lru_cache(maxsize=1024)
def fetch_record_by_doi(doi):
    """Cached record fetch."""
    doi = PersistentIdentifier.query.filter_by(
        pid_type='doi', pid_value=doi).one_or_none()
    try:
        return ZenodoRecord.get_record(doi.object_uuid)
    except Exception:
        current_app.logger.warning(
            'Could not fetch record by DOI.', exc_info=True)
        return None


@lru_cache(maxsize=1024)
def fetch_record(recid):
    """Cached record fetch."""
    return record_resolver.resolve(recid)


@lru_cache(maxsize=1024)
def fetch_record_file(recid, filename):
    """Cached record file fetch."""
    _, record = fetch_record(recid)
    return record.files[filename].obj


def get_bucket_size(client, index, agg_field, start_date=None, end_date=None):
    """Function to help us define the size for our search query.

    :param client: search client
    :param str index: prefixed search index
    :param str agg_field: aggregation field
    :param str start_date: string containing a formatted start date
    :param str end_date: string containing a formatted end date

    """
    time_range = {}
    if start_date is not None:
        time_range['gte'] = start_date
    if end_date is not None:
        time_range['lte'] = end_date

    search = Search(using=client, index=index)
    if time_range:
        search = search.filter('range', timestamp=time_range)
    search.aggs.metric('unique_values', 'cardinality', field=agg_field)

    result = search.execute()
    unique_values = result.aggregations.unique_values.value

    # NOTE: we increase the count by 10% in order to be safe
    return int(math.ceil(unique_values + unique_values * 0.1))
