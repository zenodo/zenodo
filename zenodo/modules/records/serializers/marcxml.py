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

"""MARC21 based serializer."""

from __future__ import absolute_import, print_function

from dojson.contrib.to_marc21.utils import dumps

from .dojson import DoJSONSerializer


class MARCXMLSerializer(DoJSONSerializer):
    """DoJSON based MARCXML serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records due to high memory usage.
    """

    def __init__(self, dojson_model, xslt_filename=None, schema_class=None):
        """."""
        self.xslt_filename = xslt_filename
        self.schema_class = schema_class
        super(MARCXMLSerializer, self).__init__(dojson_model)

    def dump(self, obj):
        """Dump object."""
        if self.schema_class:
            obj = self.schema_class().dump(obj).data
        return super(MARCXMLSerializer, self).dump(obj)

    def serialize(self, pid, record, links=None):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links: Dictionary of links to add to response.
        """
        return dumps(
            self.transform_record(pid, record),
            xslt_filename=self.xslt_filename)

    def serialize_search(self, pid_fetcher, search_result, links=None):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        return dumps([
            self.transform_search_hit(
                pid_fetcher(hit['_id'], hit['_source']),
                hit)
            for hit in search_result['hits']['hits']
        ], xslt_filename=self.xslt_filename)
