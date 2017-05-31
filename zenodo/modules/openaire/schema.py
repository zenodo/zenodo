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

from collections import namedtuple

from flask import current_app
from marshmallow import Schema, fields, missing

from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers.fields import DateString

OpenAIREType = namedtuple('OpenAIREType', ('type', 'resource_type'))


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
    collectedFromId = fields.Method('get_openaire_id', required=True)
    hostedById = fields.Method('get_openaire_id')

    linksToProjects = fields.Method('get_links_to_projects')
    pids = fields.Method('get_pids')

    def _resolve_openaire_type(self, obj):
        # TODO: Move to utils.py?
        metadata = obj.get('metadata')
        obj_type = ObjectType.get_by_dict(metadata.get('resource_type'))
        if obj_type['internal_id'] == 'dataset':
            return OpenAIREType('dataset', '0021')
        else:
            return OpenAIREType('publication', '0001')

    def get_original_id(self, obj):
        """Get Original Id."""
        openaire_type = self._resolve_openaire_type(obj)
        if openaire_type.type == 'publication':
            return obj.get('metadata', {}).get('_oai', {}).get('id')
        if openaire_type.type == 'dataset':
            return obj.get('metadata', {}).get('doi')

    def get_type(self, obj):
        """Get record type."""
        return self._resolve_openaire_type(obj).type

    def get_resource_type(self, obj):
        """Get resource type."""
        return self._resolve_openaire_type(obj).resource_type

    def get_openaire_id(self, obj):
        """Get OpenAIRE Zenodo ID."""
        # TODO: Move to utils.py?
        openaire_type = self._resolve_openaire_type(obj).type
        return current_app.config['OPENAIRE_ZENODO_IDS'].get(openaire_type)

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
            # Add grant acronynm to the link:
            #   [info:eu-repo/grantAgreement/EC/FP6/027819/] + [//ICEA]
            eurepo = grant.get('identifiers', {}).get('eurepo')
            links.append('{eurepo}//{acronym}'.format(
                eurepo=eurepo, acronym=grant.get('acronym', '')))
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
        # TODO: Zenodo or DOI URL? ("zenodo.org/..." or "doi.org/...")
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
