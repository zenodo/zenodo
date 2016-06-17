# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo application factories."""

from __future__ import absolute_import

import os
import sys

from invenio_base.app import create_app_factory
from invenio_base.wsgi import create_wsgi_factory, wsgi_proxyfix
from invenio_config import create_conf_loader
from statsd import StatsClient
from werkzeug.contrib.fixers import HeaderRewriterFix
from wsgi_statsd import StatsdTimingMiddleware

from . import config

env_prefix = 'APP'

conf_loader = create_conf_loader(config=config, env_prefix=env_prefix)

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
    os.path.join(sys.prefix, 'var', 'instance')
"""Path to instance folder.

Defaults to ``<virtualenv>/var/instance/``. Can be overwritten using the
environment variable ``APP_INSTANCE_PATH``.
"""

static_folder = os.getenv(env_prefix + '_STATIC_FOLDER') or \
    os.path.join(instance_path, 'static')
"""Path to static folder.

Defaults to ``<virtualenv>/var/instance/static/``. Can be overwritten
using the environment variable ``APP_STATIC_FOLDER``
"""


def create_wsgi_statsd_factory(mounts_factories):
    """Create WSGI statsd factory."""
    wsgi_factory = create_wsgi_factory(mounts_factories)

    def create_wsgi(app, **kwargs):
        application = wsgi_factory(app, **kwargs)

        # Remove X-Forwarded-For headers because Flask-Security doesn't know
        # how to deal with them properly. Note REMOTE_ADDR has already been
        # set correctly at this point by the ``wsgi_proxyfix`` factory.
        if app.config.get('WSGI_PROXIES'):
            application = HeaderRewriterFix(
                application,
                remove_headers=['X-Forwarded-For']
            )

        host = app.config.get('STATSD_HOST')
        port = app.config.get('STATSD_PORT', 8125)
        prefix = app.config.get('STATSD_PREFIX')

        if host and port and prefix:
            client = StatsClient(prefix=prefix, host=host, port=port)
            return StatsdTimingMiddleware(application, client)
        return application
    return create_wsgi


create_celery = create_app_factory(
    'zenodo',
    config_loader=conf_loader,
    extension_entry_points=['invenio_base.apps'],
    blueprint_entry_points=['invenio_base.blueprints'],
    converter_entry_points=['invenio_base.converters'],
    instance_path=instance_path,
    static_folder=static_folder,
)
"""Create CLI/Celery application."""

create_api = create_app_factory(
    'zenodo',
    config_loader=conf_loader,
    extension_entry_points=['invenio_base.api_apps'],
    blueprint_entry_points=['invenio_base.api_blueprints'],
    converter_entry_points=['invenio_base.api_converters'],
    instance_path=instance_path,
)
"""Create Flask API application."""

create_app = create_app_factory(
    'zenodo',
    config_loader=conf_loader,
    extension_entry_points=['invenio_base.apps'],
    blueprint_entry_points=['invenio_base.blueprints'],
    converter_entry_points=['invenio_base.converters'],
    wsgi_factory=wsgi_proxyfix(
        create_wsgi_statsd_factory({'/api': create_api})),
    instance_path=instance_path,
    static_folder=static_folder,
)
"""Create Flask UI application."""
