# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Template test."""

from __future__ import print_function, absolute_import

from lxml import html

from flask import url_for

from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record


def test_header_links_exists(app, record_with_files_creation):
    """Validate that link tags to files exists in document header."""
    (pid, record, record_url) = record_with_files_creation

    base_url = url_for('invenio_records_ui.recid_files',
                       pid_value=pid.pid_value, filename='Test.pdf')

    with app.test_client() as client:
        res = client.get(record_url)

        assert res.status_code == 200
        tree = html.fromstring(res.data)
        for l in tree.xpath('//link[@rel="alternate"]'):
            if l.get('href') == base_url:
                return
    assert False, "<link> tags to files not found in record page."


def test_header_pdf_metahighwire_empty(app, db, record_with_bucket):
    """Checks that the meta tag for highwire is not existing without PDF."""
    (pid, record) = record_with_bucket
    with app.test_client() as client:
        res = client.get(url_for('invenio_records_ui.recid',
                                 pid_value=pid.pid_value))
        assert res.status_code == 200
        tree = html.fromstring(res.data)
        assert len(tree.xpath('//meta[@name="citation_pdf_url"]')) == 0


def test_header_pdf_exits_metahighwire(app, record_with_files_creation):
    """Checks that the meta tag for highwire is exists when a PDF file."""
    (pid, record, record_url) = record_with_files_creation

    with app.test_client() as client:
        res = client.get(record_url)
        assert res.status_code == 200
        tree = html.fromstring(res.data)
        assert len(tree.xpath('//meta[@name="citation_pdf_url"]')) == 1
