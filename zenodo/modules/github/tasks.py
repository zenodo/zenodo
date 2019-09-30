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

"""Zenodo GitHub tasks."""


import json
import requests
from celery import shared_task
from flask import current_app


class GithubAsclepiasBrokerError(Exception):
    """Github Asclepias Broker Error for the API."""


def send_event_to_asclepias_broker(data):
    token = current_app.config("ZENODO_ASCLEPIAS_BROKER_API_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    response = requests.post(
        current_app.config("ZENODO_ASCLEPIAS_BROKER_EVENT_ENDPOINT"),
        headers=headers,
        data=data,
        verify=False,
    )

    if not response.ok:
        raise GithubAsclepiasBrokerError("Failed to send event to Asclepias Broker")

    return response

@shared_task(
    ignore_result=True, max_retries=5, default_retry_delay=60 * 60, rate_limit="100/m"
)
def send_github_event(deposit_metadata, release_payload):
    """Send GitHub events to the broker."""
    # TODO: Add first_version logic
    # TODO: modify information fecthing
    conceptdoi = deposit_metadata["conceptdoi"]
    doi = deposit_metadata["doi"]
    tag_url = u"https://github.com/{0}/tree/{1}".format(
        release_payload["repository"]["full_name"],
        release_payload["release"]["tag_name"],
    )
    repo_url = release_payload["repository"]["svn_url"]
    publication_date = deposit_metadata["publication_date"]
    doi_publication_date = ""

    data = [
        {
            "Source": {
                "Identifier": {"ID": doi, "IDScheme": "doi"},
                "Type": {"Name": "unknown"},
            },
            "RelationshipType": {
                "Name": "IsRelatedTo",
                "SubType": "IsIdenticalTo",
                "SubTypeSchema": "DataCite",
            },
            "Target": {
                "Identifier": {"ID": tag_url, "IDScheme": "url"},
                "Type": {"Name": "unknown"},
            },
            "LinkProvider": [{"Name": "Zenodo"}],
            "LinkPublicationDate": publication_date,
        },
        {
            "Source": {
                "Identifier": {"ID": conceptdoi, "IDScheme": "doi"},
                "Type": {"Name": "unknown"},
            },
            "RelationshipType": {
                "Name": "IsRelatedTo",
                "SubType": "IsIdenticalTo",
                "SubTypeSchema": "DataCite",
            },
            "Target": {
                "Identifier": {"ID": repo_url, "IDScheme": "url"},
                "Type": {"Name": "unknown"},
            },
            "LinkProvider": [{"Name": "Zenodo"}],
            "LinkPublicationDate": doi_publication_date,
        },
    ]

    try:
        send_event_to_asclepias_broker(data)

    except GithubAsclepiasBrokerError as e:
        send_github_event.retry(exc=e)
