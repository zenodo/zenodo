# -*- coding: utf-8 -*-
#
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

from __future__ import absolute_import


from flask import url_for, redirect, current_app, abort
from flask.ext.login import current_user
from invenio.modules.oauthclient.handlers import oauth2_token_setter

from ..utils import init_account


def authorized(resp, remote):
    """
    Authorized callback handler for GitHub
    """
    # User must be authenticated
    if not current_user.is_authenticated():
        return current_app.login_manager.unauthorized()

    if resp is None:
        # User rejected authorization request
        return redirect(url_for('github.rejected'))

    # Store or update acquired access token
    token = oauth2_token_setter(remote, resp)
    if token is None:
        abort(500)

    if not token.remote_account.extra_data:
        init_account(token)

    return redirect(url_for('zenodo_github.index'))
