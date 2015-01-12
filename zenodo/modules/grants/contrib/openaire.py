# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""OAI-PMH Client for Harvesting OpenAIRE grants."""

from urllib import unquote
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, MetadataReader


class OpenAireClient(Client):

    """Client for OpenAIRE OAI-PMH.

    Fixes issue with resumptionToken already being URL encoded by OpenAIRE.
    """

    oaf_reader = MetadataReader(
        fields={
            'title': (
                'textList',
                'oaf:entity/oaf:project/title/text()'),
            'acronym': (
                'textList',
                'oaf:entity/oaf:project/acronym/text()'),
            'grant_agreement_number': (
                'textList',
                'oaf:entity/oaf:project/code/text()'),
            'end_date': (
                'textList',
                'oaf:entity/oaf:project/enddate/text()'),
            'start_date': (
                'textList',
                'oaf:entity/oaf:project/startdate/text()'),
            'call_identifier': (
                'textList',
                'oaf:entity/oaf:project/callidentifier/text()'),
            'ec_project_website': (
                'textList',
                'oaf:entity/oaf:project/websiteurl/text()'),
        },
        namespaces={
            'oai': 'http://www.openarchives.org/OAI/2.0/',
            'oaf': 'http://namespace.openaire.eu/oaf',
        }
    )

    def __init__(self, url):
        """Initialize client."""
        registry = MetadataRegistry()
        registry.registerReader('oaf', self.oaf_reader)
        return super(OpenAireClient, self).__init__(
            url, metadata_registry=registry
        )

    def makeRequest(self, **kw):
        """Make HTTP request.

        Fixes issue with resumptionToken already being URL encoded by OpenAIRE.
        """
        if 'resumptionToken' in kw:
            kw['resumptionToken'] = unquote(kw['resumptionToken'])
        return super(OpenAireClient, self).makeRequest(**kw)

    def list_grants(self, set='FP7Projects'):
        """Iterate over all grants in OpenAIRE database."""
        for h, m, dummy in self.listRecords(metadataPrefix='oaf', set=set):
            yield clean_metadata(m.__dict__['_map'])


def clean_metadata(metadata_record):
    """Clean a metadata record."""
    for k in metadata_record.keys():
        v = metadata_record[k]
        if isinstance(v, list) and len(v) == 1:
            metadata_record[k] = v[0]
        elif isinstance(v, list) and len(v) == 0:
            metadata_record[k] = ""
    return metadata_record
