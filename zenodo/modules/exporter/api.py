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

"""Exporter programmatic API."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl import Q
from flask import current_app
from invenio_search.api import RecordsSearch

from .errors import FailedExportJobError
from .streams import ResultStream


class Exporter(object):
    """Export controller.

    Takes as input an index, a query, a serializer and an output writer and
    executes the export job.
    """

    def __init__(self, index='records', pid_fetcher=None, query=None,
                 resultstream_cls=ResultStream, search_cls=RecordsSearch,
                 serializer=None, writer=None, ):
        """Initialize exporter."""
        self._index = index
        self._pid_fetcher = pid_fetcher
        self._query = query
        self._resultstream_cls = resultstream_cls
        self._search_cls = search_cls
        self._serializer = serializer
        self._writer = writer

    @property
    def search(self):
        """Get Elasticsearch search instance."""
        s = self._search_cls(index=self._index)
        if self._query:
            s = s.query(Q('query_string', query=self._query))
        return s

    def run(self, progress_updater=None):
        """Run export job."""
        fp = self._writer.open()
        try:
            fp.write(self._resultstream_cls(
                self.search, self._pid_fetcher, self._serializer))
        except FailedExportJobError as e:
            current_app.logger.exception(e.message)
        finally:
            fp.close()
