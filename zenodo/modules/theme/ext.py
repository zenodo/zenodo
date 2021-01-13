# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

"""Jinja utilities for Invenio."""

from __future__ import absolute_import, print_function

import base64
import hashlib

from flask import current_app, render_template, request


def too_many_requests(e):
    """Error handler to show a 429.html page in case of a 429 error."""
    return render_template(current_app.config['THEME_429_TEMPLATE']), 429


def bad_request(e):
    """Error handler to show a 400.html page in case of a 400 error."""
    return render_template(
        current_app.config['THEME_400_TEMPLATE'], error=e), 400


def useragent_and_ip_limit_key():
    """Create key for the rate limiting."""
    ua_hash = hashlib.sha256(str(request.user_agent).encode('utf8')).digest()
    return u'{}:{}'.format(
        base64.b64encode(ua_hash).decode('ascii'), request.remote_addr
    )


class ZenodoTheme(object):
    """Zenodo theme extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        app.register_error_handler(429, too_many_requests)
        app.register_error_handler(400, bad_request)
