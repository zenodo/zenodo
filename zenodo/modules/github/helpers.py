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

from __future__ import absolute_import

from flask.ext.login import current_user
from requests import ConnectionError

from invenio.modules.oauthclient.client import oauth
from invenio.modules.oauthclient.handlers import token_getter
from invenio.modules.oauthclient.models import RemoteToken, RemoteAccount

from .utils import init_api, is_valid_token


#
# Helpers
#
def get_remote():
    """ Get the Flask-Oauthlib remote application object """
    return oauth.remote_apps['github']


def get_client_id():
    """ Get GitHub app client id """
    return get_remote().consumer_key


def get_api(user_id=None):
    """ Get an authenticated GitHub API interface """
    if user_id:
        access_token = RemoteToken.get(user_id, get_client_id()).access_token
    else:
        access_token = get_remote().get_request_token()[0]
    return init_api(access_token)


def get_token(user_id=None):
    """ Retrieve token for linked GitHub account """
    session_token = None
    if user_id is None:
        session_token = token_getter(get_remote())
    if session_token:
        token = RemoteToken.get(
            current_user.get_id(), get_client_id(),
            access_token=session_token[0]
        )
        return token
    return None


def get_account(user_id=None):
    """ Retrieve linked GitHub account """
    return RemoteAccount.get(user_id or current_user.get_id(), get_client_id())


def check_token(token):
    """ Check validity of a GitHub access token """
    try:
        return is_valid_token(get_remote(), token.access_token)
    except ConnectionError:
        # Ignore connection errors
        return True
