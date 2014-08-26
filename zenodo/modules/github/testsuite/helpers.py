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

import json
from flask import url_for
from invenio.base.globals import cfg


def tclient_request_factory(client, method, endpoint, urlargs, data,
                            is_json, headers, files, verify_ssl):
    """Make requests with test client package."""
    client_func = getattr(client, method.lower())

    if headers is None:
        headers = [('Content-Type', 'application/json')] if is_json else []

    if data is not None:
        request_args = dict(
            data=json.dumps(data) if is_json else data,
            headers=headers,
        )
    else:
        request_args = {}

    if files is not None:
        data.update({
            'file': (files['file'], data['filename']),
            'name': data['filename']
        })
        del data['filename']

    resp = client_func(
        url_for(
            endpoint,
            _external=False,
            **urlargs
        ),
        base_url=cfg['CFG_SITE_SECURE_URL'],
        **request_args
    )

    # Patch response
    resp.json = lambda: json.loads(resp.data)
    return resp
