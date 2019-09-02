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

"""Datacite to DCAT serializer."""

from __future__ import absolute_import, print_function

from lxml import etree as ET
from pkg_resources import resource_stream
from werkzeug.utils import cached_property


class DCATSerializer(object):
    """DCAT serializer for records."""

    def __init__(self, datacite_serializer):
        """."""
        self.datacite_serializer = datacite_serializer

    @cached_property
    def xslt_transform_func(self):
        """Return the DCAT XSLT transformation function."""
        with resource_stream('zenodo.modules.records',
                             'data/datacite-to-dcat-ap.xsl') as f:
            xsl = ET.XML(f.read())
        transform = ET.XSLT(xsl)
        return transform

    def transform_with_xslt(self, pid, record, search_hit=False, **kwargs):
        """Transform record with XSLT."""
        if search_hit:
            record = self.datacite_serializer.transform_search_hit(
                pid, record, **kwargs)
        else:
            record = self.datacite_serializer.transform_record(
                pid, record, **kwargs)
        dc_etree = self.datacite_serializer.schema.dump_etree(record)
        dc_namespace = self.datacite_serializer.schema.ns[None]
        dc_etree.tag = '{{{0}}}resource'.format(dc_namespace)
        dcat_etree = self.xslt_transform_func(dc_etree)
        return dcat_etree

    def _etree_tostring(self, root):
        return ET.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8',
        ).decode('utf-8')

    def serialize(self, pid, record, **kwargs):
        """Serialize a single record.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        """
        return self._etree_tostring(
            self.transform_with_xslt(pid, record, **kwargs))

    def serialize_search(self, pid_fetcher, search_result, **kwargs):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        records = []
        for hit in search_result['hits']['hits']:
            pid = pid_fetcher(hit['_id'], hit['_source'])
            dcat_etree = self.transform_with_xslt(
                pid, hit, search_hit=True, **kwargs)
            records.append(self._etree_tostring(dcat_etree))

        return '\n'.join(records)

    def serialize_oaipmh(self, pid, record):
        """Serialize a single record for OAI-PMH."""
        return self.transform_with_xslt(pid, record, search_hit=True).getroot()
