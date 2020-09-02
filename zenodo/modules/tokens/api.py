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

"""Resource access tokens API."""

from __future__ import absolute_import, print_function

from datetime import datetime, timedelta

import jwt
from flask import current_app
from invenio_oauth2server.models import Token

from .errors import ExpiredTokenError, InvalidTokenError, \
    InvalidTokenIDError, MissingTokenIDError
from .scopes import tokens_generate_scope


def decode_rat(token, sub_only=True):
    """Decodes a JWT token's payload and signer."""
    # Retrieve token ID from "kid"
    try:
        headers = jwt.get_unverified_header(token)
        access_token_id = headers.get('kid')
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    if not access_token_id:
        raise MissingTokenIDError()
    if not access_token_id.isdigit():
        raise InvalidTokenIDError()

    access_token = Token.query.get(int(access_token_id))
    if not access_token or tokens_generate_scope.id not in access_token.scopes:
        raise InvalidTokenError()

    try:
        payload = jwt.decode(
            token,
            key=access_token.access_token,
            algorithms=current_app.config.get(
                'RESOURCE_ACCESS_TOKENS_WHITELISTED_JWT_ALGORITHMS',
                ['HS256', 'HS384', 'HS512']),
            options={'require_iat': True},
        )
        token_lifetime = current_app.config.get(
            'RESOURCE_ACCESS_TOKENS_JWT_LIFETIME', timedelta(minutes=30))
        # Verify that the token is not expired based on its issue time
        issued_at = datetime.utcfromtimestamp(payload['iat'])
        if (issued_at + token_lifetime) < datetime.utcnow():
            raise ExpiredTokenError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    return access_token.user, (payload['sub'] if sub_only else payload)
