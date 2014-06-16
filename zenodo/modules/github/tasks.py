# -*- coding: utf-8 -*-
##
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""
GitHub blueprint for Zenodo
"""

from __future__ import absolute_import


from celery.utils.log import get_task_logger
import requests
import six
import sys
from flask import current_app

from invenio.celery import celery
from invenio.ext.sqlalchemy import db
from invenio.modules.webhooks.models import Event
from invenio.modules.oauth2server.models import Token as ProviderToken
from invenio.modules.oauthclient.client import oauth
#from invenio.ext.email import send_email
#from invenio.config import CFG_SITE_ADMIN_EMAIL
#from invenio.ext.template import render_template_to_string
#from invenio.modules.accounts.models import User


from .helpers import get_account, get_api
from .upload import upload
from .utils import submitted_deposition, get_zenodo_json, is_valid_sender, \
    get_contributors, init_api, revoke_token, remove_hook, get_owner


logger = get_task_logger(__name__)


@celery.task(ignore_result=True)
def disconnect_github(remote_app, access_token, extra_data):
    """ Uninstall webhooks. """
    # Note at this point the remote account and all associated data have
    # already been deleted. The celery task is passed the access_token and
    # extra_data to make some last cleanup and afterwards delete itself
    # remotely.
    remote = oauth.remote_apps[remote_app]

    try:
        gh = init_api(access_token)

        # Remove all installed hooks.
        for full_name, repo in six.iteritems(extra_data["repos"]):
            if repo.get('hook', None):
                remove_hook(gh, extra_data, full_name)
    finally:
        revoke_token(remote, access_token)


@celery.task(ignore_result=True)
def handle_github_payload(event_state, verify_sender=True):
    """ Handle incoming notification from GitHub on a new release. """
    e = Event()
    e.__setstate__(event_state)

    # Ping event
    if 'hook_id' in e.payload and 'zen' in e.payload:
        # TODO: record we sucessfully received ping event
        return

    # Get account and internal access token
    account = get_account(user_id=e.user_id)
    gh = get_api(user_id=e.user_id)
    access_token = ProviderToken.query.filter_by(
        id=account.extra_data["tokens"]["internal"]
    ).first().access_token

    # Validate payload sender
    if verify_sender and \
       not is_valid_sender(account.extra_data, e.payload):
        raise Exception("Invalid sender for payload %s for user %s" % (
            e.payload, e.user_id
        ))

    try:
        # Extra metadata from .zenodo.json and github repository
        metadata = extract_metadata(gh, e.payload)

        # Extract zip snapshot from github
        files = extract_files(e.payload)

        # Upload into Zenodo
        deposition = upload(access_token, metadata, files, publish=True)

        # TODO: Add step to update metadata of all previous records
        submitted_deposition(
            account.extra_data, e.payload['repository']['full_name'],
            deposition, e.payload['release']['tag_name']
        )
        account.extra_data.changed()
        db.session.commit()
        # Send email to user that release was included.
    except Exception as e:
        # Handle errors and possibly send user an email
        # Send email to user
        current_app.logger.exception("Failed handling GitHub payload")
        db.session.commit()
        six.reraise(*sys.exc_info())


def extract_title(release, repository):
    return release['name'] or "%s %s" % (
        repository['name'], release['tag_name']
    )


def extract_description(gh, release, repository):
    return gh.markdown(release['body']) or repository['description'] or \
        'No description provided.'


def extract_metadata(gh, payload):
    """ Extract metadata for ZENODO from a release. """
    release = payload["release"]
    repository = payload["repository"]

    defaults = dict(
        upload_type='software',
        publication_date=release['published_at'][:10],
        title=extract_title(release, repository),
        description=extract_description(gh, release, repository),
        access_right='open',
        license='other-open',
        related_identifiers=[],
    )

    # Extract metadata form .zenodo.json
    metadata = get_zenodo_json(
        gh, repository['owner']['login'], repository['name'],
        release['tag_name']
    )

    if metadata is not None:
        defaults.update(metadata)

    # Remove some fields
    for field in ['prereserve_doi', 'doi']:
        defaults.pop(field, None)

    # Add link to GitHub in related identifiers
    if 'related_identifiers' not in defaults:
        defaults['related_identifiers'] = []

    defaults['related_identifiers'].append({
        'identifier': 'https://github.com/%s/tree/%s' % (
            repository['full_name'], release['tag_name']
        ),
        'relation': 'isSupplementTo'
    })

    # Add creators if not specified
    if 'creators' not in defaults:
        defaults['creators'] = get_contributors(
            gh, repository['owner']['login'], repository['name'],
        )
        if not defaults['creators']:
            defaults['creators'] = get_owner(gh, repository['owner']['login'])
        if not defaults['creators']:
            defaults['creators'] = [dict(name='UNKNOWN', affliation='')]

    return defaults


def extract_files(payload):
    """ Extract files to download from GitHub payload. """
    release = payload["release"]
    repository = payload["repository"]

    tag_name = release["tag_name"]
    repo_name = repository["name"]

    zipball_url = release["zipball_url"]
    filename = "%(repo_name)s-%(tag_name)s.zip" % {
        "repo_name": repo_name, "tag_name": tag_name
    }

    r = requests.get(zipball_url, stream=True)
    if r.status_code != 200:
        raise Exception(
            "Could not retrieve archive from GitHub: %s" % zipball_url
        )

    return [(r.raw, filename)]
