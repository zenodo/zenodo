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

"""Record serialization."""

from __future__ import absolute_import, print_function

from dojson.contrib.to_marc21 import to_marc21
from invenio_marc21.serializers.marcxml import MARCXMLSerializer
from invenio_records_rest.serializers.datacite import DataCite31Serializer, \
    OAIDataCiteSerializer
from invenio_records_rest.serializers.dc import DublinCoreSerializer
from invenio_records_rest.serializers.json import JSONSerializer
from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from .schemas.dc import DublinCoreJSONV1
from .schemas.datacite import DataCiteSchemaJSONV1
from .schemas.json import RecordSchemaJSONV1
from .schemas.zenodo import ZenodoRecordSchemaV1
from .schemas.marcxml import RecordSchemaMARC
from .bibtex import BibTeXSerializer
from .loaders import json_marshmallow_loader

# Serializers
# ===========
#: Zenodo JSON serializer version 1.0.0
json_v1 = JSONSerializer(RecordSchemaJSONV1)
#: Zenodo JSON serialzier legacy version 1.0.0
json_v1_legacy = JSONSerializer(ZenodoRecordSchemaV1)
#: MARCXML serializer version 1.0.0
marcxml_v1 = MARCXMLSerializer(
    to_marc21, schema_class=RecordSchemaMARC)
#: BibTeX serializer version 1.0.0
bibtex_v1 = BibTeXSerializer()
#: DataCite serializer
datacite_v31 = DataCite31Serializer(DataCiteSchemaJSONV1)
#: OAI DataCite serializer
oai_datacite = OAIDataCiteSerializer(
    v31=datacite_v31,
    datacentre='CERN.ZENODO',
)
#: Dublin Core serializer
dc_v1 = DublinCoreSerializer(DublinCoreJSONV1)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, 'application/json')
#: JSON record legacy serializer for individual records.
json_v1_legacy_response = record_responsify(json_v1_legacy, 'application/json')
#: MARCXML record serializer for individual records.
marcxml_v1_response = record_responsify(marcxml_v1, 'application/marcxml+xml')
#: BibTeX record serializer for individual records.
bibtex_v1_response = record_responsify(bibtex_v1, 'application/x-bibtex')
#: DataCite v3.1 record serializer for individual records.
datacite_v31_response = record_responsify(
    datacite_v31, 'application/x-datacite+xml')
#: DublinCore record serializer for individual records.
dc_v1_response = record_responsify(dc_v1, 'application/x-dc+xml')

#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, 'application/json')
#: JSON record legacy serializer for search results.
json_v1_legacy_search = search_responsify(json_v1_legacy, 'application/json')
#: MARCXML record serializer for search records.
marcxml_v1_search = search_responsify(marcxml_v1, 'application/marcxml+xml')
#: BibTeX serializer for search records.
bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
#: DataCite v3.1 record serializer for search records.
datacite_v31_search = search_responsify(
    datacite_v31, 'application/x-datacite+xml')
#: DublinCore record serializer for search records.
dc_v1_search = search_responsify(dc_v1, 'application/x-dc+xml')

#: JSON record legacy serializer for individual records.
json_v1_legacy_loader = json_marshmallow_loader(
        ZenodoRecordSchemaV1)

# OAI-PMH record serializers.
# ===========================
#: OAI-PMH MARC21 record serializer.
oaipmh_marc21_v1 = marcxml_v1.serialize_oaipmh
#: OAI-PMH DataCite record serializer.
oaipmh_datacite_v31 = datacite_v31.serialize_oaipmh
#: OAI-PMH OAI DataCite record serializer.
oaipmh_oai_datacite = oai_datacite.serialize_oaipmh
#: OAI-PMH OAI Dublin Core record serializer.
oaipmh_oai_dc = dc_v1.serialize_oaipmh
