# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Zenodo ServceNow API"""

from __future__ import absolute_import, print_function

import json

import cern_sso
import requests
from flask import current_app


class SNOW(object):

    def __init__(self, client_id, client_secret, business_service='',
                 functional_element='', base_url='...'):
        """Initializes SNOW object."""
        self._session = None
        self._token = None
        self._headers = None

        self.business_service = business_service
        self.functional_element = functional_element
        self.base_url = base_url

        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def session(self):
        """Requests session with sign-on cookie."""
        if self._session is None:
            self._session = requests.Session()
            self._session.cookies = cern_sso.krb_sign_on(self.base_url)
        return self._session

    @property
    def token(self):
        """Requests token based on the session."""
        if self._token is None:
            _token_request = requests.post(
                self.base_url + '/oauth_token.do',
                data={
                    'grant_type': 'password',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret},
                cookies=self.session.cookies
            )
            self._token = json.loads(_token_request.text)
        return self._token

    @property
    def headers(self):
        """Creates headers including access token."""
        if self._headers is None:
            self._headers = {
                "Content-Type": 'application/json',
                "Accept": 'application/json',
                "Authorization": "Bearer " + self.token['access_token']
            }
        return self._headers

    def create_incident(self, description='', comments='', impact='',
                        urgency='', functional_category=''):
        """
        Creates an incident in SNOW based on the file integrity report

        :param str description: overview of the incident
        :param str comments: details about the incident
        :param str impact: impact of the incident. It is a number casted to a
        string according to the following scale [1-2-3] = [low-medium-high]
        :param str urgency: urgency of the incident. It is a number casted to a
        string according to the following scale [1-2-3] = [low-medium-high]
        :param str functional_category: category of the incident.
        """
        _url_create = self.base_url + '/api/now/v2/table/incident'
        self.session.post(
            _url_create,
            headers=self.headers,
            data=json.dumps({
                "short_description": description,
                "u_business_service": self.business_service,
                "u_functional_element": self.functional_element,
                "comments": comments,
                "impact": impact,
                "urgency": urgency,
                "u_functional_category": functional_category
            }),
            cookies=self.session.cookies
        )


def snow_factory():
    """Creates SNOW object with config parameters."""
    return SNOW(
        business_service=current_app.config['SNOW_BUSINESS_SERVICE'],
        functional_element=current_app.config['SNOW_FUNCTIONAL_ELEMENT'],
        base_url=current_app.config['SNOW_BASE_URL'],
        client_id=current_app.config['SNOW_CLIENT_ID'],
        client_secret=current_app.config['SNOW_CLIENT_SECRET']
    )
