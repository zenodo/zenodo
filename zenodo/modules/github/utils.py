# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import copy
import github3
import json
import pytz
import requests
from operator import itemgetter
from flask import current_app

from datetime import datetime
import dateutil.parser

from invenio.ext.sqlalchemy import db
from invenio.base.globals import cfg
from invenio.modules.webhooks.models import CeleryReceiver
from invenio.modules.oauth2server.models import Token as ProviderToken


utcnow = lambda: datetime.now(tz=pytz.utc)
"""
UTC timestamp (with timezone)
"""

iso_utcnow = lambda: utcnow().isoformat()
"""
UTC ISO8601 formatted timestamp
"""


def parse_timestamp(x):
    """
    Parse ISO8601 formatted timestamp
    """
    dt = dateutil.parser.parse(x)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt


def init_api(access_token):
    """
    Get API interface
    """
    return github3.login(token=access_token)


def init_provider_tokens(user_id):
    """
    Create local access token used to authenticate GitHub webhook as well as
    the upload using the API.
    """
    webhook_token = ProviderToken.create_personal(
        'github-webhook',
        user_id,
        scopes=['webhooks:event'],
        is_internal=True,
    )

    internal_token = ProviderToken.create_personal(
        'github-upload',
        user_id,
        scopes=['deposit:write', 'deposit:actions'],
        is_internal=True,
    )

    return webhook_token, internal_token


def init_account(remote_token):
    """
    Setup a new GitHub account
    """
    gh = init_api(remote_token.access_token)
    ghuser = gh.user()

    # Setup local access tokens
    hook_token, internal_token = init_provider_tokens(
        remote_token.remote_account.user_id
    )

    # Initial structure of extra data
    extra_data = dict(
        login=ghuser.login,
        name=ghuser.name,
        tokens=dict(
            webhook=hook_token.id,
            internal=internal_token.id,
        ),
        repos=dict(),
        last_sync=iso_utcnow(),
    )

    # Fetch list of repositories
    sync(gh, extra_data)

    # Store extra data
    remote_token.remote_account.extra_data = extra_data
    db.session.commit()


def sync(gh, extra_data, sync_hooks=True):
    """
    Helper method to sync list of repositories
    """
    repo_data = dict(
        hook=None,
        description="",
        depositions=[],
        errors=None,
    )
    login = extra_data["login"]

    existing_set = set(extra_data['repos'].keys())
    new_set = set()

    for u in [login] + [x.login for x in gh.iter_orgs()]:
        for r in gh.iter_user_repos(u, type='owner', sort='full_name'):
            # Add if not in list
            if r.full_name not in extra_data["repos"]:
                extra_data["repos"][r.full_name] = copy.copy(repo_data)
            # Update description
            extra_data["repos"][r.full_name]["description"] = r.description
            new_set.add(r.full_name)

            # # TODO:
            # if sync_hooks:
            #     for h in r.iter_hooks():
            #         if h.name == 'web' and 'url' in h.config:
            #             h.config['url'] ==

    # Remove repositories no longer available in github
    for full_name in (existing_set-new_set):
        del extra_data["repos"][full_name]

    # Update last sync
    extra_data['last_sync'] = iso_utcnow()


def remove_hook(gh, extra_data, full_name):
    """
    Remove an existing webhook
    """
    owner, repo = full_name.split("/")
    hook_id = extra_data["repos"][full_name]["hook"]

    if hook_id:
        ghrepo = gh.repository(owner, repo)
        if ghrepo:
            hook = ghrepo.hook(hook_id)
            if not hook or (hook and hook.delete()):
                extra_data["repos"][full_name]["hook"] = None
                return True
    return False


def create_hook(gh, extra_data, full_name):
    """
    Create a new webhook
    """
    owner, repo = full_name.split("/")
    webhook_token = ProviderToken.query.filter_by(
        id=extra_data['tokens']['webhook']
    ).first()
    config = dict(
        url=CeleryReceiver.get_hook_url(
            cfg['GITHUB_WEBHOOK_RECEIVER_ID'],
            webhook_token.access_token
        ),
        content_type='json',
        secret=cfg['GITHUB_SHARED_SECRET'],
        insecure_ssl="1" if cfg['GITHUB_INSECURE_SSL'] else "0",
    )

    ghrepo = gh.repository(owner, repo)
    if ghrepo:
        try:
            hook = ghrepo.create_hook(
                "web",  # GitHub identifier for webhook service
                config,
                events=["release"],
            )
            if hook:
                extra_data["repos"][full_name]["hook"] = hook.id
                return True
        except github3.GitHubError as e:
            # Check if hook is already installed
            for m in e.errors:
                if m["code"] == "custom" and m["resource"] == "Hook":
                    for h in ghrepo.iter_hooks():
                        if h.config.get('url', '') == config['url']:
                            extra_data["repos"][full_name]["hook"] = h.id
                            h.edit(
                                config=config, events=["release"], active=True
                            )
                            return True
    return False


def get_zenodo_json(gh, owner, repo_name, ref):
    """
    Get the .zenodo.json file
    """
    try:
        content = gh.repository(owner, repo_name).contents(
            '.zenodo.json', ref=ref
        )
        if not content:
            # File does not exists in the given ref
            return None
        return json.loads(content.decoded)
    except Exception:
        current_app.logger.exception("Failed to decode .zenodo.json.")
        # Problems decoding the file
        return None


def get_owner(gh, owner):
    """ Get owner of repository as a creator. """
    try:
        u = gh.user(owner)
        name = u.name or u.login
        company = u.company or ''
        return [dict(name=name, affliation=company)]
    except Exception:
        current_app.logger.exception("Failed to get GitHub owner")
        return None


def get_contributors(gh, owner, repo_name):
    """
    Get list of contributors to a repository
    """
    try:
        contrib_url = gh.repository(owner, repo_name).contributors_url

        r = requests.get(contrib_url)
        if r.status_code == 200:
            contributors = r.json()

            def get_author(contributor):
                r = requests.get(contributor['url'])
                if r.status_code == 200:
                    data = r.json()
                    return dict(
                        name=(data['name'] if 'name' in data and data['name']
                              else data['login']),
                        affiliation=(data['company'] if 'company' in data
                                     else ''),
                    )

            # Sort according to number of contributions
            contributors.sort(key=itemgetter('contributions'))
            contributors.reverse()
            contributors = map(
                get_author,
                filter(lambda x: x['type'] == 'User', contributors)
            )
            contributors = filter(lambda x: x is not None, contributors)

            return contributors
    except Exception:
        current_app.logger.exception("Failed to get GitHub contributors.")
        return None


def is_valid_token(remote, access_token):
    """
    Check validity of a GitHub access token

    GitHub requires the use of Basic Auth to query token validity.
    200 - valid token
    404 - invalid token
    """
    r = requests.get(
        "%(base)s/applications/%(client_id)s/tokens/%(access_token)s" % {
            "client_id": remote.consumer_key,
            "access_token": access_token,
            "base": cfg['GITHUB_BASE_URL']
        },
        auth=(remote.consumer_key, remote.consumer_secret)
    )

    return r.status_code == 200


def revoke_token(remote, access_token):
    """
    Revokes an access token
    """
    r = requests.delete(
        "%(base)s/applications/%(client_id)s/tokens/%(access_token)s" % {
            "client_id": remote.consumer_key,
            "access_token": access_token,
            "base": cfg['GITHUB_BASE_URL']
        },
        auth=(remote.consumer_key, remote.consumer_secret)
    )

    return r.status_code == 200


def is_valid_sender(extra_data, payload):
    return payload['repository']['full_name'] in extra_data['repos']


def submitted_deposition(extra_data, full_name, deposition, github_ref,
                         errors=None):
    deposition = dict(
        deposition_id=deposition.get('id', None),
        record_id=deposition.get('record_id', None),
        doi=deposition.get('doi', None),
        submitted=deposition.get('modified', None),
        errors=errors,
        github_ref=github_ref,  # TODO
    )
    extra_data["repos"][full_name]['depositions'].append(deposition)
