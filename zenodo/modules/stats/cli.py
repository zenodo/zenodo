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

"""Zenodo statistics CLI commands."""

import csv
import glob
import itertools
import re
import sys
from datetime import datetime as dt

import click
from flask.cli import with_appcontext
from invenio_stats.proxies import current_stats
from invenio_stats.tasks import aggregate_events, process_events
from six.moves.urllib.parse import urlparse

from zenodo.modules.records.resolvers import record_resolver
from zenodo.modules.stats.utils import extract_event_record_metadata

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

PY3 = sys.version_info[0] == 3


def chunkify(iterable, n):
    """Create equally sized tuple-chunks from an iterable."""
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def parse_record_url(url):
    """Parses a recid and filename from a record-like URL."""
    record_url = urlparse(url)
    assert record_url.hostname.lower().endswith('zenodo.org'), 'non-Zenodo url'
    match = re.match(
        # matches "/record/(123)", "/record/(123)/export", etc
        r'^\/record\/(?P<recid>\d+)'
        # matches "/record/(123)/files/(some.pdf)"
        r'(?:\/files\/(?P<filename>.+)$)?',
        record_url.path).groupdict()
    return match.get('recid'), match.get('filename')


@lru_cache(maxsize=1024)
def fetch_record(recid):
    """Cached record fetch."""
    return record_resolver.resolve(recid)


@lru_cache(maxsize=1024)
def fetch_record_file(recid, filename):
    """Cached record file fetch."""
    _, record = fetch_record(recid)
    return record.files[filename].obj


def build_common_event(record, data):
    """Build common fields of a stats event from a record and request data."""
    return dict(
        timestamp=dt.utcfromtimestamp(float(data['timestamp'])).isoformat(),
        referrer=data['referrer'],
        ip_address=data['ipAddress'],
        user_agent=data['userAgent'],
        user_id=None,
        **extract_event_record_metadata(record)
    )


def build_record_view_event(data):
    """Build a 'record-view' event from request data."""
    try:
        recid, _ = parse_record_url(data['url'])
        assert recid, 'no recid in url'
        _, record = fetch_record(recid)
    except Exception:
        return

    return build_common_event(record, data)


def build_file_download_event(data):
    """Build a 'file-download' event from request data."""
    try:
        recid, filename = parse_record_url(data['url'])
        assert recid and filename, 'no recid and filename in url'
        _, record = fetch_record(recid)
        obj = fetch_record_file(recid, filename)
    except Exception:
        return

    return dict(
        bucket_id=str(obj.bucket_id),
        file_id=str(obj.file_id),
        file_key=obj.key,
        size=obj.file.size,
        **build_common_event(record, data)
    )


EVENT_TYPE_BUILDERS = {
    'record-view': build_record_view_event,
    'file-download': build_file_download_event,
}


@click.group()
def stats():
    """Statistics commands."""


@stats.command('import')
@click.argument('event-type', type=click.Choice(EVENT_TYPE_BUILDERS.keys()))
@click.argument('csv-dir', type=click.Path(file_okay=False, resolve_path=True))
@click.option('--chunk-size', '-s', type=int, default=100)
@with_appcontext
def import_piwik_events(event_type, csv_dir, chunk_size):
    """Import stats events from a directory of CSV files.

    Available event types: "file-download", "record-view"

    The following columns should always be present:

    \b
    - ipAddress
    - userAgent
    - url ("https://zenodo.org/record/1234/files/article.pdf")
    - timestamp (1388506249)
    - referrer ("Google", "example.com", etc)
    """
    csv_files = glob.glob(csv_dir + '/*.csv')
    with click.progressbar(csv_files, len(csv_files)) as csv_files_bar:
        for csv_path in csv_files_bar:
            with open(csv_path, 'r' if PY3 else 'rb') as fp:
                reader = csv.DictReader(fp, delimiter=',')
                events = filter(
                    None, map(EVENT_TYPE_BUILDERS[event_type], reader))
                for event_chunk in chunkify(events, chunk_size):
                    current_stats.publish(event_type, event_chunk)
    click.secho(
        'Run the "invenio_stats.tasks.process_events" to index the events...',
        fg='yellow')


@stats.command('process-events')
@click.argument('event-types', nargs=-1)
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def _process_events(event_types, eager):
    """Process stats events.

    Event types:

    \b
    - record-view
    - file-download
    """
    if eager:
        process_events.apply((event_types,), throw=True)
    else:
        process_events.delay(event_types)


@stats.command('aggregate-events')
@click.argument('aggregation-types', nargs=-1)
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def _aggregate_events(aggregation_types, eager):
    """Process stats aggregations.

    Aggregation types:

    \b
    - file-download-agg
    - record-view-agg
    """
    if eager:
        aggregate_events.apply((aggregation_types,), throw=True)
    else:
        aggregate_events.delay(aggregation_types)
