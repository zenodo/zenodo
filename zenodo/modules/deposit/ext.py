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

"""ZenodoDeposit module."""

from __future__ import absolute_import, print_function

from invenio_deposit.signals import post_action
from invenio_indexer.signals import before_record_index

from . import config
from .indexer import index_versioned_record_siblings, indexer_receiver
from .receivers import datacite_register_after_publish, \
    openaire_direct_index_after_publish, sipstore_write_files_after_publish


class ZenodoDeposit(object):
    """Zenodo deposit extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)
        self.register_signals(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        @app.before_first_request
        def deposit_redirect():
            from .views import legacy_index, new
            app.view_functions['invenio_deposit_ui.index'] = legacy_index
            app.view_functions['invenio_deposit_ui.new'] = new

        app.extensions['zenodo-deposit'] = self

    @staticmethod
    def register_signals(app):
        """Register Zenodo Deposit signals."""
        before_record_index.connect(indexer_receiver, sender=app, weak=False)
        post_action.connect(datacite_register_after_publish, sender=app,
                            weak=False)
        post_action.connect(index_versioned_record_siblings, sender=app,
                            weak=False)
        post_action.connect(openaire_direct_index_after_publish, sender=app,
                            weak=False)
        post_action.connect(sipstore_write_files_after_publish, sender=app,
                            weak=False)

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_'):
                app.config.setdefault(k, getattr(config, k))
