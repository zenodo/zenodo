# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo OpenaAIRE-JSON schema."""

from __future__ import absolute_import, print_function

from flask import current_app
from marshmallow import Schema, fields, missing

from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers.fields import DateString

from .helpers import openaire_datasource_id, openaire_original_id


class RecordSchemaOpenAIREJSON(Schema):
    """Schema for records in OpenAIRE-JSON.

    OpenAIRE Schema: https://www.openaire.eu/schema/1.0/oaf-result-1.0.xsd
    OpenAIRE Vocabularies: http://api.openaire.eu/vocabularies
    """

    originalId = fields.Method('get_original_id', required=True)
    title = fields.Str(attribute='metadata.title', required=True)
    description = fields.Str(attribute='metadata.description')
    url = fields.Method('get_url', required=True)

    authors = fields.List(fields.Str(attribute='name'),
                          attribute='metadata.creators')

    type = fields.Method('get_type')
    resourceType = fields.Method('get_resource_type', required=True)
    language = fields.Str(attribute='metadata.language')

    licenseCode = fields.Method('get_license_code', required=True)
    embargoEndDate = DateString(attribute='metadata.embargo_date')

    publisher = fields.Method('get_publisher')
    collectedFromId = fields.Method('get_datasource_id', required=True)
    hostedById = fields.Method('get_datasource_id')

    linksToProjects = fields.Method('get_links_to_projects')
    pids = fields.Method('get_pids')

    def _openaire_type(self, obj):
        return ObjectType.get_by_dict(
            obj.get('metadata', {}).get('resource_type')
        ).get('openaire')

    def get_original_id(self, obj):
        """Get Original Id."""
        oatype = self._openaire_type(obj)
        if oatype:
            return openaire_original_id(
                obj.get('metadata', {}),
                oatype['type']
            )[1]
        return missing

    def get_type(self, obj):
        """Get record type."""
        oatype = self._openaire_type(obj)
        if oatype:
            return oatype['type']
        return missing

    def get_resource_type(self, obj):
        """Get resource type."""
        oatype = self._openaire_type(obj)
        if oatype:
            return oatype['resourceType']
        return missing

    def get_datasource_id(self, obj):
        """Get OpenAIRE datasouce identifier."""
        return openaire_datasource_id(obj.get('metadata')) or missing

    # Mapped from: http://api.openaire.eu/vocabularies/dnet:access_modes
    LICENSE_MAPPING = {
        'open': 'OPEN',
        'embargoed': 'EMBARGO',
        'restricted': 'RESTRICTED',
        'closed': 'CLOSED',
    }

    def get_license_code(self, obj):
        """Get license code."""
        metadata = obj.get('metadata')
        return self.LICENSE_MAPPING.get(
            metadata.get('access_right'), 'UNKNOWN')

    def get_links_to_projects(self, obj):
        """Get project/grant links."""
        metadata = obj.get('metadata')
        grants = metadata.get('grants', [])
        links = []
        for grant in grants:
            eurepo = grant.get('identifiers', {}).get('eurepo', '')
            if eurepo:
                links.append('{eurepo}/{title}/{acronym}'.format(
                    eurepo=eurepo,
                    title=grant.get('title', '').replace('/', '%2F'),
                    acronym=grant.get('acronym', '')))
        return links or missing

    def get_pids(self, obj):
        """Get record PIDs."""
        metadata = obj.get('metadata')
        pids = [{'type': 'oai', 'value': metadata['_oai']['id']}]
        if 'doi' in metadata:
            pids.append({'type': 'doi', 'value': metadata['doi']})
        return pids

    def get_url(self, obj):
        """Get record URL."""
        return current_app.config['ZENODO_RECORDS_UI_LINKS_FORMAT'].format(
            recid=obj['metadata']['recid'])

    def get_publisher(self, obj):
        """Get publisher."""
        m = obj['metadata']
        imprint_publisher = m.get('imprint', {}).get('publisher')
        if imprint_publisher:
            return imprint_publisher
        part_publisher = m.get('part_of', {}).get('publisher')
        if part_publisher:
            return part_publisher
        if m.get('doi', '').startswith('10.5281/'):
            return 'Zenodo'
        return missing
