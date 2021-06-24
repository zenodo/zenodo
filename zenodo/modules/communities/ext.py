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

"""ZenodoCommunities module."""

from __future__ import absolute_import, print_function

from invenio_communities.signals import community_created, \
    inclusion_request_created

from zenodo.modules.spam.utils import check_and_handle_spam

from . import config
from .receivers import send_inclusion_request_webhook, \
    send_record_accepted_webhook
from .signals import record_accepted


class ZenodoCommunities(object):
    """Zenodo communities extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.register_signals(app)
        app.extensions['zenodo-communities'] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_COMMUNITIES'):
                app.config.setdefault(k, getattr(config, k))

    @staticmethod
    def register_signals(app):
        """Register Zenodo Deposit signals."""
        community_created.connect(
            community_spam_checking_receiver, sender=app, weak=False)
        inclusion_request_created.connect(
            send_inclusion_request_webhook, sender=app, weak=False)
        record_accepted.connect(
            send_record_accepted_webhook, sender=app, weak=False)


def community_spam_checking_receiver(sender, community):
    """Receiver for spam checking of newly created communities."""
    check_and_handle_spam(community=community)
