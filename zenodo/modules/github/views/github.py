# -*- coding: utf-8 -*-
##
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""
GitHub blueprint for Zenodo.


1) Go to GitHub and create a new application
   *) Set Authorization callback URL to
      http://localhost:4000/oauth/authorized/github/
   *) Add the keys to configuration
        OAUTH_GITHUB = dict(
            consumer_key="changeme",
            consumer_secret="changeme",
        )

2) Add to invenio.cfg:

WEBHOOKS_DEBUG_RECEIVER_URLS = {
    'github': 'http://github.<yourid>.ultrahook.com?access_token=%(token)s',
}

3) Start Ultrahook

ultrahook github 4000/api/hooks/receivers/github/events/

"""

from __future__ import absolute_import


import pytz
import humanize
from dateutil.parser import parse
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, current_app, abort
from flask.ext.login import login_required
from flask.ext.menu import register_menu
from flask.ext.breadcrumbs import register_breadcrumb

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db
from invenio.ext.sslify import ssl_required
from invenio.modules.webhooks.models import Receiver, CeleryReceiver

from ..tasks import handle_github_payload
from ..utils import sync, utcnow, parse_timestamp, remove_hook, create_hook
from ..helpers import get_api, get_token, get_account, check_token


blueprint = Blueprint(
    'zenodo_github',
    __name__,
    static_folder="../static",
    template_folder="../templates",
    url_prefix="/account/settings/github",
)


#
# Before first request loaders
#
@blueprint.before_app_first_request
def register_webhook():
    """ Setup webhook endpoint for github notifications. """
    Receiver.register(
        current_app.config.get('GITHUB_WEBHOOK_RECEIVER_ID'),
        CeleryReceiver(handle_github_payload)
    )


#
# Template filters
#
@blueprint.app_template_filter('naturaltime')
def naturaltime(val):
    """ Get humanized version of time. """
    val = parse(val)
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    return humanize.naturaltime(now - val)


#
# Views
#
@blueprint.route('/')
@ssl_required
@login_required
@register_menu(
    blueprint, 'settings.github',
    _('<i class="fa fa-github fa-fw"></i> GitHub'),
    order=10,
    active_when=lambda: request.endpoint.startswith("zenodo_github.")
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.github', _('GitHub'))
def index():
    """ Display list of repositories. """
    token = get_token()
    ctx = dict(connected=False)

    if token is not None and check_token(token):
        # The user is authenticated and the token we have is still valid.
        extra_data = token.remote_account.extra_data

        # Check if sync is needed - should probably not be done here
        last_sync = parse_timestamp(extra_data["last_sync"])
        now = utcnow()
        yesterday = now - timedelta(days=1)

        if last_sync < yesterday:
            sync(get_api(), extra_data)
            token.remote_account.extra_data.changed()
            db.session.commit()

        ctx.update({
            "connected": True,
            "repos": extra_data['repos'],
            "name": extra_data['login'],
            "user_id": token.remote_account.user_id,
            "last_sync": humanize.naturaltime(now - last_sync),
        })

    return render_template("github/index.html", **ctx)


@blueprint.route('/faq')
@ssl_required
@login_required
def faq():
    """  Display FAQ. """
    return render_template("github/faq.html")


@blueprint.route('/rejected/')
@ssl_required
@login_required
def rejected(resp):
    """ View for when user rejects request to connect to github. """
    return render_template("github/rejected.html")


@blueprint.route('/hook/', methods=["POST", "DELETE"])
@ssl_required
@login_required
def hook():
    """
    Install or remove GitHub webhook
    """
    repo = request.json["repo"]
    account = get_account()
    extra_data = account.extra_data

    if repo not in extra_data["repos"]:
            abort(404)

    if request.method == 'DELETE':
        if remove_hook(get_api(), extra_data, repo):
            account.extra_data.changed()
            db.session.commit()
            return "", 204
        else:
            abort(400)
    elif request.method == 'POST':
        if create_hook(get_api(), extra_data, repo):
            account.extra_data.changed()
            db.session.commit()
            return "", 201
        else:
            abort(400)
    else:
        abort(400)


@blueprint.route('/sync/', methods=["POST"])
@ssl_required
@login_required
def sync_repositories():
    account = get_account()
    sync(get_api(), account.extra_data)
    account.extra_data.changed()
    db.session.commit()

    ctx = dict(
        connected=True,
        repos=account.extra_data['repos'],
        name=account.extra_data['login'],
        user_id=account.user_id,
        last_sync=humanize.naturaltime(
            utcnow() - parse_timestamp(account.extra_data['last_sync'])
        ),
    )

    return render_template("github/index.html", **ctx)
