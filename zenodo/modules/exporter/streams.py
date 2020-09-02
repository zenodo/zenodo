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

"""Result stream serialization."""

from __future__ import absolute_import, print_function

import bz2

from .errors import FailedExportJobError


class ResultStream(object):
    """Stream of serialized records for a search.

    The result stream implements a simple iterator that iterates over all
    records in a specific search and serializes each record. In addition, it
    emulates a stream API with the ``read()`` method, so that the serialized
    records can be written to an output.

    :param search: Elasticsearch DSL search instance configured for specific
        index.
    :param pid_fetcher: Persistent identifier fetcher that matches configured
        index.
    :param serializer: Serializer that supports export (i.e. the serialize
        must have implement the API ``serialize_exporter(pid, record)``).
    """

    def __init__(self, search, pid_fetcher, serializer):
        """Initialize result stream."""
        self.pid_fetcher = pid_fetcher
        self.search = search
        self.serializer = serializer
        self._iter = None
        self.failed_record_ids = []

    def __next__(self):
        """Fetch next serialized record."""
        # Initialize iterator (i.e. execute scroll search), if not already
        # initialized.
        if self._iter is None:
            self._iter = self.search.scan()
        # Fetch next hit.
        hit = next(self._iter)
        # Serialize and return hit.
        result = ''
        try:
            result = self.serializer.serialize_exporter(
                self.pid_fetcher(hit.meta.id, hit),
                dict(_source=hit._d_, _version=0),
            )
        except Exception as e:
            self.failed_record_ids.append(hit.meta.id)

        return result

    def __iter__(self):
        """Iterator."""
        return self

    def next(self):
        """Python 2.x compatibility function."""
        return self.__next__()

    def read(self, *args):
        """Read next serialized record for search results.

        The method will return an empty string for repeated calls once all
        records have been read.
        """
        try:
            return next(self)
        except StopIteration:
            if self.failed_record_ids:
                # raise an exception with the list of not serialized records
                raise FailedExportJobError(record_ids=self.failed_record_ids)
            return b''


class BZip2ResultStream(ResultStream):
    """BZip2 compressed stream of serialized records for a search.

    Works like :py:data:`ResultStream`, except that the output is compressed
    with BZip2.
    """

    def __init__(self, *args, **kwargs):
        """Initialize result stream."""
        super(BZip2ResultStream, self).__init__(*args, **kwargs)
        self.compressor = bz2.BZ2Compressor()

    def __next__(self):
        """Fetch next serialized bzip2 compressed chunk of records(s)."""
        try:
            data = None
            while not data:
                data = self.compressor.compress(
                    super(BZip2ResultStream, self).__next__()
                )
            return data
        except StopIteration:
            # Once we have read all records, make sure we flush the data left
            # in compressor. Repeated calls to flush will raise a ValueError.
            try:
                return self.compressor.flush()
            except ValueError:
                raise StopIteration
