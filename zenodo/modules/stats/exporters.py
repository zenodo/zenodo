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

"""Zenodo stats exporters."""

import datetime
import json
import uuid
import zlib
from copy import deepcopy

import requests
from dateutil.parser import parse as dateutil_parse
from elasticsearch_dsl import Search
from flask import current_app
from invenio_cache import current_cache
from invenio_pidstore.errors import PIDDeletedError
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from six.moves.urllib.parse import urlencode

from zenodo.modules.records.serializers.schemas.common import ui_link_for
from zenodo.modules.stats.errors import PiwikExportRequestError
from zenodo.modules.stats.utils import chunkify, fetch_record


class PiwikExporter:
    """Events exporter."""

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
                elif update_bookmark is True:
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
        cvar = json.dumps({'1': ['oaipmhID', oai]})
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


class DataciteStatisticsCLient:
    """Datactite Statistics Client exporter."""

    _DEFAULT_HEADER = {
        "report-id": "DSR",
        "release": "rd1",
        "report-name": "dataset report"
    }

    _COMPRESSED_REPORT_EXCEPTIONS_HEADER = {
        "code": 69,
        "severity": "warning",
        "message": "Report is compressed using gzip",
        "help-url": "https://github.com/datacite/sashimi",
        "data": "usage data needs to be uncompressed",
    }

    def __init__(self, url, jwt, chunk_size=50000, report_header_values=None):
        """Initializes DataciteStatisticsClient object."""
        self.url = url
        self.jwt = jwt
        self.chunk_size = chunk_size
        self.report_header_values = report_header_values
        self.request_headers = {
            "content-type": "application/gzip",
            "content-encoding": "gzip",
            "accept": "gzip",
            "authorization": "Bearer " + self.jwt,
        }

    def _build_report_header(self, start_date, end_date):
        report_header = deepcopy(self._DEFAULT_HEADER)
        report_header.update(self.report_header_values)
        report_header.setdefault("exceptions", [])
        report_header["exceptions"].append(
            [deepcopy(self._COMPRESSED_REPORT_EXCEPTIONS_HEADER)]
        )
        report_header['reporting-period'] = {
            'end-date': end_date,
            'begin-date': start_date
        }
        report_header['created'] = datetime.datetime.now().isoformat()
        return report_header

    def _compress_payload(self, payload):
        return zlib.compress(json.dumps(payload).encode("utf_8"))

    def send(self, start_date, end_date, datasets, report_header=None):
        """
        Send statistic report to Datacite.

        :param str start_date: ISO formatted date
        :param str end_date: ISO formatted date
        :param dict datasets: statistics of the specified period
        :param dict report_header: metadata of the statistic report
        """
        id_ = str(uuid.uuid4())
        report_header = report_header or\
            self._build_report_header(start_date, end_date)
        report = {'report-header': report_header}
        report['id'] = id_
        report['report-datasets'] = []

        response = requests.put(
            self.url + '/{}'.format(id_),
            headers=self.request_headers,
            data=self._compress_payload(report)
        )

        for dataset_chunk in chunkify(datasets, self.chunk_size):
            report['report-datasets'] = dataset_chunk
            requests.post(
                url=self.url,
                headers=self.request_headers,
                data=self._compress_payload(report)
            )
