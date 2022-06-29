# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2022 CERN.
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

"""Pytest configuration."""

import pytest
from flask import current_app


@pytest.fixture
def use_safelist_config(app, api):
    """Activate webhooks config."""

    # NOTE: Not optimal for applying the config patch to both apps, but works
    for _app in (app, api):
        old_value_safelist_index = _app.config.pop(
            'ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD')
        old_value_search_safelist = current_app.config.pop(
            'ZENODO_RECORDS_SEARCH_SAFELIST')

        _app.config['ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD'] = 2
        _app.config['ZENODO_RECORDS_SEARCH_SAFELIST'] = True

    yield

    for _app in (app, api):

        _app.config['ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD'] = \
            old_value_safelist_index
        _app.config['ZENODO_RECORDS_SEARCH_SAFELIST'] = \
            old_value_search_safelist
