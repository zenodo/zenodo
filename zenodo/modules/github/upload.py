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

import json
import requests
from flask import url_for


from invenio.base.globals import cfg


class ZenodoApiException(Exception):
    pass


class ZenodoApiWarning(ZenodoApiException):
    pass


class ZenodoApiError(ZenodoApiException):
    pass


def requests_request_factory(method, endpoint, urlargs, data, is_json, headers,
                             files, verify_ssl):
    """
    Make requests with request package
    """
    client_func = getattr(requests, method.lower())

    if headers is None:
        headers = [('Content-Type', 'application/json')] if is_json else []

    if data is not None:
        request_args = dict(
            data=json.dumps(data) if is_json else data,
            headers=dict(headers),
        )
    else:
        request_args = {}

    if files is not None:
        request_args['files'] = files

    return client_func(
        url_for(
            endpoint,
            _external=True,
            _scheme='https',
            **urlargs
        ),
        verify=verify_ssl,
        **request_args
    )


class ZenodoClient(object):
    def __init__(self, access_token, ssl_verify=True, request_factory=None):
        self.access_token = access_token
        self.ssl_verify = ssl_verify
        self.request_factory = request_factory or requests_request_factory

    def make_request(self, method, endpoint, urlargs={}, data=None,
                     is_json=True, headers=None, files=None):

        urlargs['access_token'] = self.access_token

        return self.request_factory(
            method, endpoint, urlargs, data, is_json, headers, files,
            self.ssl_verify
        )

    def get(self, *args, **kwargs):
        return self.make_request("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.make_request("post", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.make_request("put", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.make_request("delete", *args, **kwargs)


def upload(access_token, metadata, files, publish=False, request_factory=None):
    """
    Zenodo Upload
    """
    client = ZenodoClient(
        access_token,
        ssl_verify=False,
        request_factory=request_factory,
    )

    # Create deposition
    r = client.post('depositionlistresource', data={})
    if r.status_code != 201:
        raise ZenodoApiError("Could not create deposition.")

    deposition_id = r.json()['id']

    # Upload a file
    for fileobj, filename in files:
        r = client.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=deposition_id),
            is_json=False,
            data={'filename': filename},
            files={'file': fileobj},
        )
        if r.status_code != 201:
            raise ZenodoApiWarning(deposition_id, "Could not add file")

    # Set metadata (being set here to ensure file is fetched)
    r = client.put(
        'depositionresource',
        urlargs=dict(resource_id=deposition_id),
        data={"metadata": metadata}
    )
    if r.status_code != 200:
        if r.status_code == 400:
            errors = r.json()
        raise ZenodoApiWarning(deposition_id, "Problem with metadata", errors)

    if publish:
        r = client.post(
            'depositionactionresource',
            urlargs=dict(resource_id=deposition_id, action_id='publish'),
        )
        if r.status_code != 202:
            raise ZenodoApiWarning(deposition_id, "Could not publish deposition")

        return r.json()
    else:
        r = client.get(
            'depositionresource',
            urlargs=dict(resource_id=deposition_id),
        )
        if r.status_code != 200:
            raise ZenodoApiWarning(deposition_id, "Could not get deposition")
        return r.json()
