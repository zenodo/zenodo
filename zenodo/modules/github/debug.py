# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2015 CERN.
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

from flask import current_app


from invenio.modules.webhooks.models import Event
from invenio.modules.oauth2server.models import Token as ProviderToken

from zenodo.modules.github.helpers import get_account, get_api
from zenodo.modules.github.utils import is_valid_sender
from zenodo.modules.github.tasks import extract_metadata, extract_files, \
    handle_github_payload


def payload_debug(event_state):
    """"Debug a GitHub payload."""
    res = dict()
    try:
        e = Event()
        e.__setstate__(event_state)
        res['event'] = e

        current_app.try_trigger_before_first_request_functions()

        account = get_account(user_id=e.user_id)
        res['account'] = account

        gh = get_api(user_id=e.user_id)
        res['gh'] = gh

        access_token = ProviderToken.query.filter_by(
            id=account.extra_data["tokens"]["internal"]
        ).first().access_token
        res['access_token'] = access_token

        res['is_valid_sender'] = is_valid_sender(account.extra_data, e.payload)

        res['metadata'] = extract_metadata(gh, e.payload)

        res['files'] = extract_files(e.payload, account.tokens[0].access_token)
    finally:
        pass
    return res


def payload_rerun(event_state):
    """Rerun event notification from GitHub.

    .. warning::
        You risk reuploading an existing upload.
    """
    return handle_github_payload.delay(event_state)
