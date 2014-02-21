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
"""

from __future__ import absolute_import

import json

from flask import current_app
import requests

from invenio.ext.sqlalchemy import db
from invenio.ext.email import send_email
from invenio.config import CFG_SITE_ADMIN_EMAIL
from invenio.ext.template import render_template_to_string
from invenio.modules.accounts.models import User
from invenio.modules.webhooks.models import Event
from invenio.celery import celery
from zenodo.ext.oauth import oauth

from .models import OAuthTokens

ZENODO_API = "https://zenodo-dev.cern.ch/api"


def create_empty_deposition(api_key, payload, user):
    errors = []
    headers = {"Content-Type": "application/json"}

    repository = payload["repository"]
    repository_name = repository["full_name"]

    r = requests.post(
        "%(api)s/deposit/depositions?apikey=%(api_key)s" % {"api": ZENODO_API, "api_key": api_key},
        data="{}",
        headers=headers,
        verify=False
    )

    # Check if the deposition was created. When errors, make note on the extra_data and notify owner.
    # TODO: Email notification to owner
    if r.status_code != 201:

        # The deposition was not created. Make note in extra_data and notify user
        errors.append(
            {"message": "Deposition was not created."}
        )
        user.extra_data["repos"][repository_name]["errors"] = errors
        user.extra_data.update()

        db.session.commit()

    return {
        "response": r,
        "errors": errors
    }


def append_deposition_metadata(api_key, payload, user, user_email, deposition_id):
    errors = []
    headers = {"Content-Type": "application/json"}

    # At this point we need to get metadata. Since we require the user to include a .zenodo.json file in the repository,
    # we'll fetch it here, or prompt the user to supply metadata via an email notification.

    # Format the raw url from the release payload
    zenodo_json_path = payload["release"]["html_url"]
    zenodo_json_path = zenodo_json_path.replace("github.com", "raw.github.com")
    zenodo_json_path = zenodo_json_path.replace("releases/tag/", '')
    zenodo_json_path += "/.zenodo.json"

    release = payload["release"]
    repository = payload["repository"]
    repository_name = repository["full_name"]

    # Get the .zenodo.json file
    r = requests.get(zenodo_json_path)
    if r.status_code == 200:
        metadata = json.loads(r.text)

        previous_doi = user.extra_data["repos"][repository_name].get("doi")
        if previous_doi:
            metadata["related_identifiers"] = [{
                "relation": "isSupplementTo",
                "identifier": previous_doi
            }]

        zenodo_metadata = { "metadata": metadata }
        r = requests.put(
            "%(api)s/deposit/depositions/%(deposition_id)s?apikey=%(api_key)s" \
            % {"api": ZENODO_API, "deposition_id": deposition_id, "api_key": api_key},
            data=json.dumps(zenodo_metadata),
            headers=headers,
            verify=False
        )

        # The metadata file contains errors
        if r.status_code == 400:

            # Metadata was not attached due to malformed .zenodo.json file. Append to errors and notify via email.
            errors = errors + r.json()["errors"]

            send_email(
                CFG_SITE_ADMIN_EMAIL,
                user_email,
                subject="Metadata Needed For Deposition",
                content=render_template_to_string(
                    "github/email_zenodo_json.html"
                )
            )

    else:

        # There's no zenodo.json file in the repository. Append to errors and
        # notify owner for additional metadata.
        errors.append(
            {"message": "Missing .zenodo.json metadata file from repository."}
        )

        # Notify user when there is no .zenodo.json file in the repository.
        send_email(
            CFG_SITE_ADMIN_EMAIL,
            user_email,
            subject="Metadata Needed For Deposition",
            content=render_template_to_string(
                "github/email_zenodo_json.html"
            )
        )

    return {
        "response": r,
        "errors": errors
    }

# TODO: Notify user via email
def append_deposition_file(api_key, payload, deposition_id, user_email):
    errors = []
    headers = {"Content-Type": "application/json"}

    release = payload["release"]
    repository = payload["repository"]
    repository_name = repository["full_name"]

    # Download the archive
    archive_url = release["zipball_url"]
    archive_name = "%(repo_name)s-%(tag_name)s.zip" % {"repo_name": repository["name"], "tag_name": release["tag_name"]}

    r = requests.get(archive_url, stream=True)
    if r.status_code == 200:

        # Append the file to the deposition
        data = {'filename': archive_name}
        files = {"file": r.raw}

        r = requests.post(
            "%(api)s/deposit/depositions/%(deposition_id)s/files?apikey=%(api_key)s" % \
            {"api": ZENODO_API, "deposition_id": deposition_id, "api_key": api_key},
            data=data,
            files=files,
            verify=False
        )

        if r.status_code != 201:
            errors.append(
                {"message": "Could not upload the archive to Zenodo."}
            )
    else:

        # There was trouble getting the archive from GitHub
        errors.append(
            {"message": "Could not retrieve the archive from GitHub."}
        )

    return {
        "response": r,
        "errors": errors
    }

def publish_deposition(api_key, payload, user, errors, deposition_id, user_email):

    repository = payload["repository"]
    repository_name = repository["full_name"]

    if len(errors) == 0:

        r = requests.post(
            "%(api)s/deposit/depositions/%(deposition_id)s/actions/publish?apikey=%(api_key)s" % \
            {"api": ZENODO_API, "deposition_id": deposition_id, "api_key": api_key},
            verify=False
        )

        if r.status_code == 202:
            user.extra_data["repos"][repository_name]["doi"] = r.json()["doi"]
            user.extra_data["repos"][repository_name]["modified"] = r.json()["modified"]
            user.extra_data["repos"][repository_name].pop("errors", None)
            user.extra_data["repos"][repository_name].pop("deposition_id", None)
            user.extra_data.update()

            db.session.commit()

            user.extra_data.update()
            db.session.commit()

            return True

        errors.append(
            {"message": "Deposition could not be published to Zenodo."}
        )

    # Add to extra_data
    user.extra_data["repos"][repository_name]["deposition_id"] = deposition_id
    user.extra_data["repos"][repository_name]["errors"] = errors
    user.extra_data.update()
    db.session.commit()

    return False

# TODO: Send requests checking SSL certificate (zenodo-dev certificate expired!)
# TODO: Ensure duplicate releases are not created.
@celery.task(ignore_result=True)
def create_deposition(event_state):
    ZENODO_API_KEY = current_app.config["ZENODO_API_KEY"]
    remote = oauth.remote_apps['github']

    e = Event()
    e.__setstate__(event_state)

    user_id = e.user_id
    user_email = User.query.filter_by(id=user_id).first().email
    payload = e.payload
    user = OAuthTokens.query.filter_by(user_id=user_id).filter_by(
        client_id=remote.consumer_key
    ).first()

    # GitHub sends a small test payload when the hook is created. Avoid creating
    # a deposition from it.
    if 'hook_id' in payload:
        return json.dumps({"state": "hook-added"})

    errors = []

    #
    #   Step 1: Create an empty deposition
    #
    status = create_empty_deposition(ZENODO_API_KEY, payload, user)

    if status["response"].status_code != 201:
        return json.dumps(
            {"errors": status["errors"]}
        )
    errors = errors + status["errors"]

    #
    #   Step 2: Get and attach metadata to deposition
    #
    # The deposition has successfully been created.
    deposition_id = status["response"].json()["id"]
    status = append_deposition_metadata(ZENODO_API_KEY, payload, user, user_email, deposition_id)
    errors = errors + status["errors"]

    #
    #   Step 3: Get the archive file
    #
    status = append_deposition_file(ZENODO_API_KEY, payload, deposition_id, user_email)
    errors = errors + status["errors"]

    #
    #   Step 4: Publish to Zenodo for wicked software preservation!
    #

    # TODO: Might need to handle other response codes in publish_deposition ...
    status = publish_deposition(ZENODO_API_KEY, payload, user, errors, deposition_id, user_email)
    if status:
        msg = {"state": "deposition successfully published"}
    else:
        msg = {"state": "deposition not successful"}

    return json.dumps(msg)

