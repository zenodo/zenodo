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

import mimetypes

import idutils
from flask import has_request_context
from flask_security import current_user
from invenio_records.api import Record
from lxml import etree as ET
from pkg_resources import resource_stream
from werkzeug.utils import cached_property

from zenodo.modules.records.serializers.schemas.common import ui_link_for

from ..permissions import has_read_files_permission


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

    def _add_files(self, root, files, record):
        """Add files information via distribution elements."""
        ns = root.nsmap

        def download_url(file, record):
            url = ui_link_for('record_file', id=record['recid'], filename=file['key'])
            return url, {
                '{{{rdf}}}resource'.format(**ns): url
            }

        def media_type(file, _):
            return mimetypes.guess_type(file['key'])[0], None

        def byte_size(file, _):
            return str(file['size']), None

        def access_url(_, record):
            return idutils.to_url(record['doi'], 'doi', url_scheme='https'), None

        files_fields = {
            '{{{dcat}}}downloadURL': download_url,
            '{{{dcat}}}mediaType': media_type,
            '{{{dcat}}}byteSize': byte_size,
            '{{{dcat}}}accessURL': access_url,
            # TODO: there's also "spdx:checksum", but it's not in the W3C spec yet
        }

        for f in files:
            dist_wrapper = ET.SubElement(
                root[0], '{{{dcat}}}distribution'.format(**ns))
            dist = ET.SubElement(
                dist_wrapper, '{{{dcat}}}Distribution'.format(**ns))

            for tag, func in files_fields.items():
                text_val, attrs_val = func(f, record)

                if text_val or attrs_val:
                    el = ET.SubElement(dist, tag.format(**ns))
                    if text_val:
                        el.text = text_val
                    if attrs_val:
                        el.attrib.update(attrs_val)

    def _etree_tostring(self, root):
        return ET.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8',
        ).decode('utf-8')

    def transform_with_xslt(self, pid, record, search_hit=False, **kwargs):
        """Transform record with XSLT."""
        files_data = None
        if search_hit:
            dc_record = self.datacite_serializer.transform_search_hit(
                pid, record, **kwargs)
            if '_files' in record['_source']:
                files_data = record['_source']['_files']
            elif '_files' in record:
                files_data = record['_files']

        else:
            dc_record = self.datacite_serializer.transform_record(
                pid, record, **kwargs)
            # for single-record serialization check file read permissions
            if isinstance(record, Record) and '_files' in record:
                if not has_request_context() or has_read_files_permission(
                        current_user, record):
                    files_data = record['_files']

        dc_etree = self.datacite_serializer.schema.dump_etree(dc_record)
        dc_namespace = self.datacite_serializer.schema.ns[None]
        dc_etree.tag = '{{{0}}}resource'.format(dc_namespace)
        dcat_etree = self.xslt_transform_func(dc_etree).getroot()

        # Inject files in results (since the XSLT can't do that by default)
        if files_data:
            self._add_files(
                root=dcat_etree,
                files=files_data,
                record=(record['_source'] if search_hit else record),
            )

        return dcat_etree

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
        if isinstance(record["_source"], Record):
             return self.transform_with_xslt(pid, record["_source"], search_hit=False)
        else:
             return self.transform_with_xslt(pid, record, search_hit=True)
