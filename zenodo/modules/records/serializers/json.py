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

"""Marshmallow based JSON serializer for records."""

from __future__ import absolute_import, print_function

from flask import current_app, json, request

from .marshmallow import MarshmallowSerializer


class JSONSerializer(MarshmallowSerializer):
    """Marshmallow based JSON serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    @staticmethod
    def _format_args():
        """Get JSON dump indentation and separates."""
        if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and \
           not request.is_xhr:
            return dict(
                indent=2,
                separators=(', ', ': '),
            )
        else:
            return dict(
                indent=None,
                separators=(',', ':'),
            )

    def serialize(self, pid, record, links=None):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links: Dictionary of links to add to response.
        """
        return json.dumps(
            self.transform_record(pid, record),
            **self._format_args())

    def serialize_search(self, pid_fetcher, search_result, links=None):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        return json.dumps(dict(
            hits=dict(
                hits=[self.transform_search_hit(
                    pid_fetcher(hit['_id'], hit['_source']),
                    hit,
                ) for hit in search_result['hits']['hits']],
                total=search_result['hits']['total'],
            ),
            links=links or {},
            aggregations=search_result['aggregations'],
        ), **self._format_args())
