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

"""Cache for Zenodo."""

from __future__ import absolute_import, print_function

from flask.ext.cache import Cache

from .bccache import RedisBytecodeCache


class ZenodoCache(object):
    """Zenodo cache extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.cache = Cache(app)
        self.app = app
        self.enable_jinja_cache()
        app.extensions['zenodo-cache'] = self

    def enable_jinja_cache(self):
        """Enable Jinja cache."""
        self.app.jinja_env.bytecode_cache = RedisBytecodeCache(
            self.app, self.cache)
        self.app.jinja_options = dict(
            self.app.jinja_options,
            auto_reload=False,
            cache_size=-1,
            bytecode_cache=RedisBytecodeCache(self.app, self.cache))
