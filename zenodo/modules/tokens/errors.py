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

"""Resource access tokens module errors."""

from __future__ import absolute_import, print_function

from invenio_rest.errors import RESTException


class ResourceAccessTokenError(RESTException):
    """Resource access token base error class."""

    code = 400


class MissingTokenIDError(ResourceAccessTokenError):
    """Resource access token for missing token ID."""

    description = 'Missing "kid" key with personal access token ID in JWT header.'


class InvalidTokenIDError(ResourceAccessTokenError):
    """Resource access token error for invalid token ID."""

    description = '"kid" JWT header value not a valid personal access token ID.'


class InvalidTokenError(ResourceAccessTokenError):
    """Resource access token for invalid token."""

    description = 'The token is invalid.'


class ExpiredTokenError(InvalidTokenError):
    """Resource access token error for expired token."""

    description = 'The token is expired.'
