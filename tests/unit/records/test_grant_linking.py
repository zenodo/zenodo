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

"""Grant linking tests."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_records.api import Record


def test_grant_linking(app, db, minimal_record, grant_records):
    """Test grant linking."""
    minimal_record['grants'] = [{
        '$ref': 'http://dx.zenodo.org/grants/10.13039/501100000780::282896'}]
    record = current_app.extensions['invenio-records'].replace_refs(
        Record.create(minimal_record))
    assert record['grants'][0]['funder']['name'] == 'European Commission'
    record.validate()
