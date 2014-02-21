# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""
GitHub blueprint for Zenodo


1) Go to GitHub and create a new application
   *) Set Authorization callback URL to http://localhost:4000/account/settings/github/connected
   *) Add the keys to configuration
        ZENODO_GITHUB_CLIENT_ID = ""
        ZENODO_GITHUB_CLIENT_SECRET = ""


"""

from __future__ import absolute_import

import os
import json
import pytz
import dateutil
from dateutil.parser import parse
from datetime import datetime, timedelta

import humanize
import requests
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, current_app
from flask.ext.login import current_user

from invenio.ext.sqlalchemy import db
from invenio.ext.email import send_email
from invenio.modules.oauth2server.provider import oauth2
from invenio.config import CFG_SITE_ADMIN_EMAIL, CFG_SITE_NAME
from invenio.ext.template import render_template_to_string
from invenio.modules.accounts.models import User
from invenio.modules.oauth2server.models import Token
from invenio.modules.webhooks.models import Receiver, CeleryReceiver
from zenodo.ext.oauth import oauth
from flask.ext.login import login_required
from invenio.ext.sslify import ssl_required
from flask.ext.breadcrumbs import register_breadcrumb
from flask.ext.menu import register_menu
from invenio.base.i18n import _
from ..models import OAuthTokens
from ..tasks import create_deposition


remote = oauth.remote_apps['github']
blueprint = Blueprint(
    'zenodo_github',
    __name__,
    static_folder="../static",
    template_folder="../templates",
    url_prefix="/account/settings/github",
)


@blueprint.before_app_first_request
def register_webhook():
    Receiver.register(
        current_app.config.get('GITHUB_WEBHOOK_ID'),
        CeleryReceiver(create_deposition)
    )

@blueprint.app_template_filter('naturaltime')
def naturaltime(val):
    val = parse(val)
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    return humanize.naturaltime(now - val)


def get_repositories(user, github_login=None):
    """Helper method to get a list of current user's repositories from GitHub."""
    r = remote.get("users/%(username)s/repos?type=owner&sort=full_name" %
                   {"username": github_login or session["github_login"]})

    repo_data = r.data

    def get_repo_name(repo):
        return repo["full_name"]

    def get_repo_data(repo):
        return {"hook": None, "description": repo["description"]}

    repo_names = map(get_repo_name, repo_data)
    repo_data = map(get_repo_data, repo_data)
    repos = dict(
        zip(repo_names, repo_data)
    )

    if user is not None:
        extra_data = user.extra_data

        # Map the existing data with the fresh dump from GitHub
        for name, description in repos.iteritems():
            if name in extra_data["repos"]:
                repos[name] = extra_data["repos"][name]

    return {
        "repos_last_sync": str(datetime.now()),
        "repos": repos
    }


@blueprint.route('/')
@ssl_required
@login_required
@register_menu(
    blueprint, 'settings.github',
    _('<i class="fa fa-github fa-fw"></i> GitHub'),
    order=10,
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.github', _('GitHub'))
def index():
    context = {"connected": False}

    # Check if user has already authorized GitHub
    user = OAuthTokens.query \
        .filter_by(
            user_id=current_user.get_id(),
            client_id=remote.consumer_key
        ).first()

    if user is not None:

        # The user has previously been authenticated. Check if the token is still valid.
        # GitHub requires the use of Basic Auth to query token validity. Valid
        # responses return 200.
        r = requests.get(
            "https://api.github.com/applications/%(client_id)s/tokens/%(access_token)s" %
            {"client_id": remote.consumer_key,
                "access_token": user.access_token},
            auth=(remote.consumer_key, remote.consumer_secret)
        )

        if r.status_code == 200:
            # The user is authenticated and the token we have is still valid.
            # Render GitHub settings page.
            extra_data = user.extra_data

            # Add information to session
            session["github_token"] = (user.access_token, '')
            session["github_login"] = extra_data['login']

            # Check the date of the last repo sync
            last_sync = datetime.strptime(
                extra_data["repos_last_sync"],
                "%Y-%m-%d %H:%M:%S.%f"
            )
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            if last_sync < yesterday:
                repos = get_repositories(user)
                user.extra_data.update(repos)
                db.session.commit()

            context["connected"] = True
            context["repos"] = extra_data['repos']
            context["name"] = extra_data['login']
            context["user_id"] = user.user_id
            context["last_sync"] = humanize.naturaltime(
                datetime.now() - last_sync)

    return render_template("github/index.html", **context)

@blueprint.route('/connect')
def connect():
    return remote.authorize(
        callback=url_for('.connected', _external=True)
    )

@blueprint.route('/connected')
@remote.authorized_handler
def connected(resp):
    current_user_id = current_user.get_id()

    # TODO: Better error handling. If GitHub auth fails, we'll get a Bad
    # Request (400)
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    # Store the GitHub access token on the session
    github_token = resp['access_token']
    session['github_token'] = (github_token, '')

    # Check if the user has previously created a GitHub OAuth token
    user = OAuthTokens.query \
        .filter_by( user_id=current_user.get_id() ) \
        .filter_by( client_id=remote.consumer_key ) \
        .first()
    if user is None:

        # Get user data
        resp = remote.get('user')
        github_login = resp.data['login']
        github_name = resp.data['name']

        # Create a Zenodo personal access token
        zenodo_token = Token.create_personal(
            'github',
            current_user_id,
            scopes=['webhooks:event']
        )

        extra_data = get_repositories(user, github_login=github_login)
        extra_data.update({
            "login": github_login,
            "name": github_name,
            "zenodo_token_id": zenodo_token.id
        })

        # Put user's GitHub info in database
        o = OAuthTokens(
            client_id=remote.consumer_key,
            user_id=current_user.get_id(),
            access_token=github_token,
            extra_data=extra_data
        )
        db.session.add(o)
    else:
        # User has previously connected to the GitHub client. Update the token.
        user.access_token = github_token
        github_login = user.extra_data['login']
        github_name = user.extra_data['name']

    db.session.commit()

    return redirect(url_for('.index'))

@blueprint.route('/remove-github-hook', methods=["POST"])
def remove_github_hook():
    status = {"status": False}
    repo = request.json["repo"]

    # Get the hook id from the database
    user = OAuthTokens.query.filter_by(user_id=current_user.get_id()).filter_by(
        client_id=remote.consumer_key).first()
    hook_id = user.extra_data["repos"][repo]["hook"]

    resp = remote.delete(
        "repos/%(full_name)s/hooks/%(hook_id)s" % {
            "full_name": repo, "hook_id": hook_id},
    )

    if resp.status == 204:
        # The hook has successfully been removed by GitHub, update the status
        # and DB
        status["status"] = True

        user.extra_data["repos"][repo]["hook"] = None
        user.extra_data.update()
        db.session.commit()

    return json.dumps(status)

@blueprint.route('/create-github-hook', methods=["POST"])
def create_github_hook():
    status = {"status": False}
    repo = request.json["repo"]

    user = OAuthTokens.query.filter_by(user_id=current_user.get_id()).filter_by(
        client_id=remote.consumer_key).first()
    github_login = user.extra_data["login"]
    zenodo_token_id = Token.query.filter_by(
        id=user.extra_data["zenodo_token_id"]).first().access_token

    data = {
        "name": "web",
        "config": {
            "url": CeleryReceiver.get_hook_url('github', zenodo_token_id),
            "content_type": "json"
        },
        "events": ["release"],
        "active": True
    }

    resp = remote.post(
        "repos/%(full_name)s/hooks" % {"full_name": repo},
        format='json',
        data=data
    )

    if resp.status == 201:
        # Hook was created, updated the status and database
        status["status"] = True

        user.extra_data["repos"][repo]["hook"] = resp.data["id"]
        user.extra_data.update()
        db.session.commit()

    return json.dumps(status)

@blueprint.route('/sync', methods=["GET"])
def sync_repositories():
    user = OAuthTokens.query.filter_by(user_id=current_user.get_id()).filter_by(
        client_id=remote.consumer_key).first()

    repos = get_repositories(user)
    user.extra_data.update(repos)
    db.session.commit()
    
    # Check the date of the last repo sync
    last_sync = datetime.strptime(
        user.extra_data["repos_last_sync"],
        "%Y-%m-%d %H:%M:%S.%f"
    )
    
    context = {}
    context["connected"] = True
    context["repos"] = user.extra_data['repos']
    context["name"] = user.extra_data['login']
    context["user_id"] = user.user_id
    context["last_sync"] = humanize.naturaltime(
        datetime.now() - last_sync
    )

    return render_template("github/index.html", **context)


@remote.tokengetter
def get_oauth_token():
    return session.get('github_token')
