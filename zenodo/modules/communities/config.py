# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015-2021 CERN.
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

"""Configuration for Zenodo Communities."""

from __future__ import absolute_import, print_function

ZENODO_COMMUNITIES_NOTIFY_DISABLED = ['zenodo', ]
"""Communities with disabled email notification on requests."""

ZENODO_COMMUNITIES_AUTO_ENABLED = True
"""Automatically add and request to communities upon publishing."""

ZENODO_COMMUNITIES_AUTO_REQUEST = ['zenodo', ]
"""Communities which are to be auto-requested upon first publishing."""

ZENODO_COMMUNITIES_REQUEST_IF_GRANTS = ['ecfunded', ]
"""Communities which are to be auto-requested if record has grants."""

ZENODO_COMMUNITIES_ADD_IF_GRANTS = []
"""Communities which are to be auto-added if record has grants."""

ZENODO_COMMUNITIES_WEBHOOKS = {}
"""Webhook sending configurations for community inclusion requests.

Example configuration:

.. code-block:: python

    ZENODO_COMMUNITIES_WEBHOOKS = {
        'astrophysics': {
            'example_recipient_id': {
                'url': 'https://example.org/webhooks/zenodo',
                'headers': {
                    'X-Custom-Auth': 'foobar',
                },
                'params': {
                    'token': 'some-token',
                }
            },
        }
    }
"""
