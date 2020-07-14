# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018-2019 CERN.
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

"""Zenodo stats exporters."""

import calendar
import copy
import datetime
import gzip
import json
import math

import requests
from dateutil.parser import parse as dateutil_parse
from elasticsearch_dsl import Search
from flask import current_app
from invenio_cache import current_cache
from invenio_pidstore.errors import PIDDeletedError
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from six.moves.urllib.parse import urlencode

from zenodo.modules.records.minters import is_local_doi
from zenodo.modules.records.serializers.schemas.common import ui_link_for
from zenodo.modules.stats.errors import PiwikExportRequestError
from zenodo.modules.stats.utils import chunkify, fetch_record, \
    fetch_record_by_doi, get_bucket_size


class PiwikExporter:
    """Export events to OpenAIRE's Piwik instance."""

    def run(self, start_date=None, end_date=None, update_bookmark=True):
        """Run export job."""
        if start_date is None:
            bookmark = current_cache.get('piwik_export:bookmark')
            if bookmark is None:
                msg = 'Bookmark not found, and no start date specified.'
                current_app.logger.warning(msg)
                return
            start_date = dateutil_parse(bookmark) if bookmark else None

        time_range = {}
        if start_date is not None:
            time_range['gte'] = start_date.replace(microsecond=0).isoformat()
        if end_date is not None:
            time_range['lte'] = end_date.replace(microsecond=0).isoformat()

        events = Search(
            using=current_search_client,
            index=build_alias_name('events-stats-*')
        ).filter(
            'range', timestamp=time_range
        ).sort(
            {'timestamp': {'order': 'asc'}}
        ).params(preserve_order=True).scan()

        url = current_app.config['ZENODO_STATS_PIWIK_EXPORTER'].get('url', None)
        token_auth = current_app.config['ZENODO_STATS_PIWIK_EXPORTER'] \
            .get('token_auth', None)
        chunk_size = current_app.config['ZENODO_STATS_PIWIK_EXPORTER']\
            .get('chunk_size', 0)

        for event_chunk in chunkify(events, chunk_size):
            query_strings = []
            for event in event_chunk:
                if 'recid' not in event:
                    continue
                try:
                    query_string = self._build_query_string(event)
                    query_strings.append(query_string)
                except PIDDeletedError:
                    pass

            payload = {
                'requests': query_strings,
                'token_auth': token_auth
            }

            res = requests.post(url, json=payload)

            # Failure: not 200 or not "success"
            content = res.json() if res.ok else None
            if res.status_code == 200 and content.get('status') == 'success':
                if content.get('invalid') != 0:
                    msg = 'Invalid events in Piwik export request.'
                    info = {
                        'begin_event_timestamp': event_chunk[0].timestamp,
                        'end_event_timestamp': event_chunk[-1].timestamp,
                        'invalid_events': content.get('invalid')
                    }
                    current_app.logger.warning(msg, extra=info)
                elif update_bookmark:
                    current_cache.set('piwik_export:bookmark',
                                      event_chunk[-1].timestamp,
                                      timeout=-1)
            else:
                msg = 'Invalid events in Piwik export request.'
                info = {
                    'begin_event_timestamp': event_chunk[0].timestamp,
                    'end_event_timestamp': event_chunk[-1].timestamp,
                }
                raise PiwikExportRequestError(msg, export_info=info)

    def _build_query_string(self, event):
        id_site = current_app.config['ZENODO_STATS_PIWIK_EXPORTER']\
            .get('id_site', None)
        url = ui_link_for('record_html', id=event.recid)
        visitor_id = event.visitor_id[0:16]
        _, record = fetch_record(event.recid)
        oai = record.get('_oai', {}).get('id')
        cvar = json.dumps({'1': ['oaipmhID', oai],
                           '2': ['volume', event.to_dict().get('volume')],
                           '3': ['pub_date', event.publication_date],
                           '4': ['version', event.revision_id],
                           '5': ['is_machine', 1 if event.is_machine else 0]
                           })
        action_name = record.get('title')[:150]  # max 150 characters

        params = dict(
            idsite=id_site,
            rec=1,
            url=url,
            _id=visitor_id,
            cid=visitor_id,
            cvar=cvar,
            cdt=event.timestamp,
            urlref=event.referrer,
            action_name=action_name
        )

        if event.to_dict().get('country'):
            params['country'] = event.country.lower()
        if event.to_dict().get('file_key'):
            params['url'] = ui_link_for('record_file', id=event.recid,
                                        filename=event.file_key)
            params['download'] = params['url']

        return '?{}'.format(urlencode(params, 'utf-8'))


def _next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


class DataCiteReportExporter:
    """Export stats report to DataCite."""

    def run(self, start_date=None, update_bookmark=True):
        """Run export job."""
        today = datetime.date.today()
        end_year, end_month = today.year, today.month

        if start_date:
            year, month = start_date.split('-')
        else:
            bookmark = current_cache.get('datacite_export:bookmark')
            if not start_date and bookmark is None:
                current_app.logger.warning(
                    'Bookmark not found, and no start date specified.')
                return
            year, month = map(int, bookmark.split('-'))
            # Bookmark is for the last sent report, we need the next month
            year, month = _next_month(year, month)

        # Send only complete months until now
        while (year, month) < (end_year, end_month):
            for report in generate_usage_reports(year, month):
                send_usage_report(report)
            # Update the bookmark for the last month that was sent
            if update_bookmark:
                current_cache.set(
                    'datacite_export:bookmark',
                    '{}-{}'.format(year, month),
                    timeout=-1,
                )
            year, month = _next_month(year, month)


def send_usage_report(report):
    """Send a DataCite usage statistics report."""
    headers = {
        'Content-Encoding': 'gzip',
        'Content-Type': 'application/gzip',
        'Authorization': 'Bearer {}'.format(
            current_app.config['ZENODO_STATS_DATACITE_TOKEN']),
    }
    res = requests.post(
        current_app.config['ZENODO_STATS_DATACITE_API_URL'],
        data=gzip.compress(json.dumps(report)),
        headers=headers,
    )
    if res.ok:
        current_app.logger.info(
            'DataCite report submitted successfully',
            extra={'id': res.json()['report']['id']},
        )
    else:
        current_app.error.warning(
            'DataCite report submission failed', extra=res.text)
    return res.json()


def generate_usage_reports(year, month):
    """Yield usage reports for a specific year and month."""
    last_month_day = calendar.monthrange(year, month)[1]
    begin_date = '{}-{:02d}-01'.format(year, month)
    end_date = '{}-{:02d}-{:02d}'.format(year, month, last_month_day)

    report_template = {
        "report-header": {
            "report-filters": [],
            "report-attributes": [],
            "exceptions": [{
                "code": 69,
                "severity": "warning",
                "message": "Report is compressed using gzip",
                "help-url": "https://github.com/datacite/sashimi",
                "data": "usage data needs to be uncompressed",
            }],
            "created": datetime.date.today().isoformat(),
            "reporting-period": {
                "begin-date": begin_date,
                "end-date": end_date,
            },
        },
        "report-datasets": None,
    }
    report_template['report-header'].update(
        current_app.config['ZENODO_STATS_DATACITE_REPORT_HEADER'])
    report_max_items = current_app.config.get(
        'ZENODO_STATS_DATACITE_REPORT_MAX_ITEMS', 50000)
    report_items_iter = generate_report_items(begin_date, end_date)
    for report_items_chunk in chunkify(report_items_iter, report_max_items):
        report = copy.deepcopy(report_template)
        report['report-datasets'] = report_items_chunk
        yield report


def generate_report_items(begin_date, end_date):
    """."""
    # We query "raw" usage events for calculating the statistics
    index = build_alias_name('events-stats-*')
    rounded_dt = '{}T00:00:00||/M'.format(begin_date)
    events_query = Search(
        using=current_search_client,
        index=index,
    ).filter(
        'range', timestamp={'gte': rounded_dt, 'lte': rounded_dt},
    )

    doi_bucket_size = get_bucket_size(
        current_search_client,
        index,
        agg_field='doi',
        start_date=rounded_dt,
        end_date=rounded_dt,
    )

    num_partitions = max(int(math.ceil(float(doi_bucket_size) / 10000)), 1)
    for p in range(num_partitions):

        doi_bucket = events_query.aggs.bucket(
            'doi', 'terms', field='doi', size=doi_bucket_size,
            include={'partition': p, 'num_partitions': num_partitions},
        )

        user_type_bucket = doi_bucket.bucket(
            'user_type', 'terms', field='is_machine', size=2,
        )

        # TODO: Check if country-level metrics are supported
        # country_bucket = user_type_bucket.bucket(
        #     'country', 'terms', field='country', size=300,
        # )

        views_bucket = user_type_bucket.bucket(
            'views', 'missing', field='file_key'
        )
        views_bucket.metric(
            'unique', 'cardinality',
            field='unique_session_id', precision_threshold=1000)

        downloads_bucket = user_type_bucket.bucket(
            'downloads', 'filter', exists={'field': 'file_key'},
        )
        downloads_bucket.metric(
            'unique', 'cardinality',
            field='unique_session_id', precision_threshold=1000)
        # TODO: Add when Make Data Count is integrated inti SUSHI reports
        # downloads_bucket.metric('volume', 'sum', field='size')

        results = events_query.execute(ignore_cache=True)
        for doi_result in results.aggregations.doi.buckets:
            doi = doi_result.key
            record = fetch_record_by_doi(doi)
            if not record or 'recid' not in record:  # skip if no metadata was found
                continue

            report_item = {
                'uri': 'https://zenodo.org/record/{recid}'.format(
                    recid=record['recid']),
                'dataset-id': [{'type': 'doi', 'value': doi}],
                'platform': 'Zenodo',
                'data-type': 'dataset',
            }

            publisher_info = None
            if is_local_doi(doi):
                publisher_info = \
                    current_app.config['ZENODO_STATS_LOCAL_PUBLISHER']
            else:
                try:
                    doi_prefix = doi.split('/', 1)[0]
                    publisher_info = current_app.config.get(
                        'ZENODO_STATS_DOI_PREFIX_PUBLISHERS', {})[doi_prefix]
                except Exception:
                    current_app.logger.warning(
                        'Could not get publisher information for DOI prefix',
                        exc_info=True,
                    )

            if not publisher_info:
                # TODO: Check with DataCite if we could put "dummy" values here
                continue

            report_item['publisher'] = publisher_info['name']
            report_item['publisher-id'] = []
            for id_type in ('grid', 'isni', 'ror', 'urn', 'orcid'):
                if id_type in publisher_info:
                    report_item['publisher-id'].append({
                        'type': id_type,
                        'value': publisher_info[id_type],
                    })

            pub_date = record['publication_date']
            report_item['yop'] = pub_date[:4]
            report_item['dataset-dates'] = [{
                'type': 'pub-date', 'value': pub_date
            }]
            report_item['dataset-title'] = record['title']
            report_item['dataset-contributors'] = []
            for c in record['creators']:
                report_item['dataset-contributors'].append({
                    'type': 'name', 'value': c['name'],
                })
                if c.get('orcid'):
                    report_item['dataset-contributors'].append({
                        'type': 'orcid', 'value': c['orcid'],
                    })

            if record.get('version'):
                report_item['dataset-attributes'] = [{
                    'type': 'dataset-version', 'value': record['version']
                }]

            report_item['performance'] = [{
                'period': {'begin-date': begin_date, 'end-date': end_date},
                'instance': []
            }]
            for ut in doi_result.user_type.buckets:

                access_method = 'machine' if ut.key == 1 else 'regular'
                metrics = (
                    ('total-dataset-investigations', ut.views.doc_count),
                    ('unique-dataset-investigations', ut.views.unique.value),
                    ('total-dataset-requests', ut.downloads.doc_count),
                    ('unique-dataset-requests', ut.downloads.unique.value),
                )

                for metric_type, count in metrics:
                    report_item['performance'][0]['instance'].append({
                        'count': count,
                        'metric-type': metric_type,
                        'access-method': access_method,
                    })
            yield report_item
