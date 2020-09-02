# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2020 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests for resource access tokens API."""

from datetime import datetime, timedelta

import jwt
import pytest

from zenodo.modules.tokens.api import decode_rat
from zenodo.modules.tokens.errors import ExpiredTokenError, \
    InvalidTokenError, InvalidTokenIDError, MissingTokenIDError


def _rat_gen(token, payload=None, headers=None):
    payload = {'iat': datetime.utcnow()} if payload is None else payload
    headers = {'kid': str(token.id)} if headers is None else headers
    return jwt.encode(
        payload=payload,
        key=token.access_token,
        algorithm='HS256',
        headers=headers,
    )


def test_decoding(app, write_token, rat_generate_token):
    """Test decoding a resource access token."""
    write_token = write_token['token']
    rat_generate_token = rat_generate_token['token']

    with pytest.raises(MissingTokenIDError):
        decode_rat(_rat_gen(rat_generate_token, headers={}))

    with pytest.raises(InvalidTokenIDError):
        decode_rat(_rat_gen(rat_generate_token, headers={'kid': 'invalid'}))

    with pytest.raises(InvalidTokenError):
        decode_rat(_rat_gen(rat_generate_token, headers={'kid': '99999'}))

    with pytest.raises(InvalidTokenError):
        decode_rat(_rat_gen(write_token))

    with pytest.raises(InvalidTokenError):
        decode_rat('not_a.valid_jwt')

    with pytest.raises(ExpiredTokenError):
        decode_rat(_rat_gen(
            rat_generate_token,
            # generate token issued an hour ago
            payload={'iat': datetime.utcnow() - timedelta(hours=1)}
        ))
