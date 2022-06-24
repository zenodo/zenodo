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

"""Test Spam views."""

import pytest
from flask import current_app, url_for
from helpers import login_user_via_session


def test_safelist_add_remove(
    app, db, use_safelist_config, users, full_record
):
    with app.test_client() as client:
        login_user_via_session(client, email=users[2]['email'])  # admin

        # Add to safelist
        res = client.post(
            url_for('zenodo_spam.safelist_add_remove', user_id=1),
            data={
              'action': 'post',
              'next': url_for('invenio_records_ui.recid',
                              pid_value=full_record['recid'])
            },
            follow_redirects=True
        )

        assert 'Added to safelist' in res.get_data()

        # Remove from safelist
        res = client.post(
            url_for('zenodo_spam.safelist_add_remove', user_id=1),
            data={
                'action': 'delete',
                'next': url_for('invenio_records_ui.recid',
                                pid_value=full_record['recid']),
            },
            follow_redirects=True
        )

        assert 'Removed from safelist' in res.get_data()

# TODO test search
