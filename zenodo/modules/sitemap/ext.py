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

"""Sitemap generation for Zenodo."""

from __future__ import absolute_import, print_function

from invenio_cache import current_cache
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from . import config
from .generators import generator_fns


class ZenodoSitemap(object):
    """Zenodo sitemap extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.generators = [fn for fn in generator_fns]
        app.extensions['zenodo-sitemap'] = self
        # Keep the currently stored sitemap cache keys for easy clearing
        self.cache_keys = set()

    def set_cache(self, key, value):
        """Set the sitemap cache."""
        current_cache.set(key, value, timeout=0)
        self.cache_keys.add(key)

    @staticmethod
    def get_cache(key):
        """Get the sitemap cache."""
        current_cache.get(key)

    def clear_cache(self):
        """Clear the sitemap cache."""
        for key in self.cache_keys:
            current_cache.delete(key)
        self.cache_keys = set()

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_SITEMAP_'):
                app.config.setdefault(k, getattr(config, k))

    def _generate_all_urls(self):
        """Run all generators and yield the sitemap JSON entries."""
        for generator in self.generators:
            for generated in generator():
                yield generated
