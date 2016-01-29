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

"""Serialization response factories.

Responsible for creating a HTTP response given the output of a serializer.
"""

from __future__ import absolute_import, print_function

from flask import current_app


def record_responsify(serializer, mimetype):
    """Create a Records-REST response serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    """
    def view(pid, record, code=200, headers=None):
        links = {}
        response = current_app.response_class(
            serializer.serialize(pid, record, links=links),
            mimetype=mimetype)
        response.status_code = code
        # response.headers['location'] = links['self']
        if headers is not None:
            response.headers.extend(headers)
        response.set_etag(str(record.revision_id))
        return response
    return view


def search_responsify(serializer, mimetype):
    """Create a Records-REST search result response serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    """
    def view(pid_fetcher, search_result, links=None, code=200, headers=None):
        response = current_app.response_class(
            serializer.serialize_search(
                pid_fetcher, search_result, links=links),
            mimetype=mimetype)
        response.status_code = code
        if headers is not None:
            response.headers.extend(headers)
        return response
    return view
