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

"""Test query-based OAISet updating."""

from __future__ import absolute_import, print_function

from datetime import datetime

from invenio_records.api import Record

from zenodo.modules.utils.tasks import update_search_pattern_sets


def make_rec(comm, sets):
    """Create a minimal record for Community-OAISet testing."""
    return {'communities': comm, '_oai': {'sets': sets}}


def test_oaiset_update(app, db, oaisets, es, oaiset_update_records):
    """Test query-based OAI sets updating."""
    rec_ok, rec_rm, rec_add = [Record.get_record(uuid) for uuid
                               in oaiset_update_records]
    year_now = str(datetime.now().year)
    # Assume starting conditions
    assert set(rec_ok['_oai']['sets']) == set(['extra', 'user-foobar', ])
    assert rec_ok['_oai']['updated'].startswith('1970')
    assert set(rec_rm['_oai']['sets']) == set(['extra', 'user-foobar', ])
    assert rec_rm['_oai']['updated'].startswith('1970')
    assert set(rec_add['_oai']['sets']) == set(['user-foobar', ])
    assert rec_add['_oai']['updated'].startswith('1970')

    # Run the updating task
    update_search_pattern_sets.delay()

    rec_ok, rec_rm, rec_add = [Record.get_record(uuid) for uuid
                               in oaiset_update_records]
    # After update
    assert set(rec_ok['_oai']['sets']) == set(['extra', 'user-foobar', ])
    assert rec_ok['_oai']['updated'].startswith('1970')
    assert set(rec_rm['_oai']['sets']) == set(['user-foobar', ])
    assert rec_rm['_oai']['updated'].startswith(year_now)
    assert set(rec_add['_oai']['sets']) == set(['extra', 'user-foobar', ])
    assert rec_add['_oai']['updated'].startswith(year_now)
