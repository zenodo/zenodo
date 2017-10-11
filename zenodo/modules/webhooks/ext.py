# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo webhooks module."""

from __future__ import absolute_import, print_function


from . import config


class ZenodoWebhooks(object):
    """Zenodo Webhooks extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.subscribers = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # TODO: Load from DB model in the future...
        self.subscribers.extend(
            app.config.get('ZENODO_WEBHOOKS_SUBSCRIBERS', []))

        debug_receiver_url = app.config.get(
            'ZENODO_WEBHOOKS_DEBUG_RECEIVER_URL')
        if debug_receiver_url:
            for s in self.subscribers:
                s['original_url'] = s['url']
                s['url'] = debug_receiver_url

        app.extensions['zenodo-webhooks'] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_WEBHOOKS_'):
                app.config.setdefault(k, getattr(config, k))
