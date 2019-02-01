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

"""Zenodo OpenAIRE extension."""

from __future__ import absolute_import, print_function

from collections import defaultdict

from werkzeug.utils import cached_property

from . import config


class _ZenodoOpenAIREState(object):
    """Store the OpenAIRE mappings."""

    def __init__(self, app):
        self.app = app

    @cached_property
    def openaire_communities(self):
        """Configuration for OpenAIRE communities types."""
        return self.app.config['ZENODO_OPENAIRE_COMMUNITIES']

    @cached_property
    def inverse_openaire_community_map(self):
        """Lookup for Zenodo community -> OpenAIRE community."""
        comm_map = self.openaire_communities
        items = defaultdict(list)
        for oa_comm, cfg in comm_map.items():
            for z_comm in cfg['communities']:
                items[z_comm].append(oa_comm)
        return items



class ZenodoOpenAIRE(object):
    """Zenodo OpenAIRE extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_OPENAIRE_'):
                app.config.setdefault(k, getattr(config, k))

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        state = _ZenodoOpenAIREState(app)
        self._state = app.extensions['zenodo-openaire'] = state
