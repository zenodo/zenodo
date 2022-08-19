# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017-2021 CERN.
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

"""ZenodoMetrics module."""

from __future__ import absolute_import, print_function

from flask import current_app

from . import config


class ZenodoMetrics(object):
    """Zenodo frontpage extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_METRICS'):
                app.config.setdefault(k, getattr(config, k))

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['zenodo-metrics'] = self

    @property
    def metrics_start_date(self):
        """Get get metrics start date from config."""
        return current_app.config['ZENODO_METRICS_START_DATE']
