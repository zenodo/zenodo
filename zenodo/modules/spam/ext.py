# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2020 CERN.
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

"""Support and contact module for Zenodo."""

from __future__ import absolute_import, print_function

import joblib
from celery.signals import celeryd_init
from flask import current_app

from . import config, current_spam
from .utils import DomainList


class ZenodoSpam(object):
    """Zenodo support form."""

    @property
    def model(self):
        """Spam detection model."""
        if not getattr(self, '_model', None):
            if not current_app.config.get('ZENODO_SPAM_MODEL_LOCATION'):
                model = None
            else:
                model = joblib.load(
                    current_app.config['ZENODO_SPAM_MODEL_LOCATION'])
            self._model = model
        return self._model

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.domain_forbiddenlist = DomainList(
            app.config['ZENODO_SPAM_DOMAINS_FORBIDDEN_PATH']
        )
        self.domain_safelist = DomainList(
            app.config['ZENODO_SPAM_DOMAINS_SAFELIST_PATH']
        )
        app.extensions['zenodo-spam'] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_SPAM_'):
                app.config.setdefault(k, getattr(config, k))


@celeryd_init.connect
def warm_up_cache(instance, **kwargs):
    """Preload the spam model in the celery application."""
    flask_app = instance.app.flask_app
    if flask_app.config.get('ZENODO_SPAM_MODEL_PRELOAD'):
        with flask_app.app_context():
            current_spam.model
