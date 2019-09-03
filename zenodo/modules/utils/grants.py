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

"""Grants utilities."""

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import sqlite3
from base64 import b64decode
from gzip import GzipFile
from itertools import islice, repeat
from zipfile import ZipFile

from six import BytesIO
from six.moves import zip


class OpenAIREGrantsDump(object):
    """Utility class to manage OpenAIRE grant dumps."""

    def __init__(self, path, rows_write_chunk_size=10000):
        """Initialize the OpenAIRE grants dump."""
        self.path = path
        self.rows_write_chunk_size = rows_write_chunk_size

    def _parse_grant_line(self, line):
        json_data = json.loads(line)
        body = json_data['body']['$binary']
        zip_bytes = BytesIO(b64decode(body))
        with ZipFile(zip_bytes) as zf:
            return zf.read('body').decode('utf-8')

    @property
    def _grants_iterator(self):
        with GzipFile(self.path) as gf:
            for line in gf:
                yield self._parse_grant_line(line.decode('utf-8'))

    def split(self, filepath_prefix, grants_per_file=None):
        """Dump grants into multiple SQLite files.

        :param str filepath_prefix: Path which will be used as a prefix for the
            generated SQLite files. e.g. passing ``/tmp/grants-`` will generate
            ``/tmp/grants-01.db``, ``/tmp/grants-02.db``, etc.
        :param int grants_per_file: The maximum number of grants that will be
            stored per file. If ``None``, only one file will be used.
        """
        file_idx = 0
        grants_iter = self._grants_iterator
        file_row_count = 1
        while file_row_count > 0:
            filepath = '{0}{1:02d}.db'.format(filepath_prefix, file_idx)
            file_row_count = self.write(
                filepath, islice(grants_iter, grants_per_file))
            file_idx += 1
            if file_row_count > 0:
                yield filepath, file_row_count

    def write(self, filepath, grants, chunk_size=None):
        """Write grants to an SQLite file.

        In case no rows were written to the file, the file is removed.

        :param str filepath: Path to the SQLite file to be written.
        :param grants: Iterable of grants that will be written to the
            database.
        :return: Number of rows written to the file.
        """
        chunk_size = chunk_size or self.rows_write_chunk_size
        with sqlite3.connect(filepath) as conn:
            conn.execute('CREATE TABLE grants (data text, format text)')
            total_rows_inserted = 0
            rows_inserted = 1
            while rows_inserted > 0:
                rows_inserted = conn.executemany(
                    'INSERT INTO grants VALUES (?, ?)',
                    zip(islice(grants, chunk_size), repeat('xml'))
                ).rowcount
                if rows_inserted > 0:
                    total_rows_inserted += rows_inserted
        if total_rows_inserted <= 0:  # delete a zero-rows file
            os.unlink(filepath)
        return total_rows_inserted
