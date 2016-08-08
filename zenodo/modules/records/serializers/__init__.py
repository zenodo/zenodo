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
from invenio_records_rest.serializers.citeproc import CiteprocSerializer
from invenio_records_rest.serializers.datacite import DataCite31Serializer, \
    OAIDataCiteSerializer
from invenio_records_rest.serializers.dc import DublinCoreSerializer
from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from .bibtex import BibTeXSerializer
from .files import files_responsify
from .json import ZenodoJSONSerializer as JSONSerializer
from .legacyjson import DepositLegacyJSONSerializer, LegacyJSONSerializer
from .schemas.csl import RecordSchemaCSLJSON
from .schemas.datacite import DataCiteSchemaV1
from .schemas.dc import DublinCoreV1
from .schemas.json import DepositSchemaV1, RecordSchemaV1
from .schemas.legacyjson import FileSchemaV1, GitHubRecordSchemaV1, \
    LegacyRecordSchemaV1
from .schemas.marc21 import RecordSchemaMARC21

# Serializers
# ===========
#: Zenodo JSON serializer version 1.0.0
json_v1 = JSONSerializer(RecordSchemaV1, replace_refs=True)
#: Zenodo Deposit JSON serializer version 1.0.0
deposit_json_v1 = JSONSerializer(DepositSchemaV1, replace_refs=True)
#: Zenodo legacy deposit JSON serialzier version 1.0.0
legacyjson_v1 = LegacyJSONSerializer(
    LegacyRecordSchemaV1, replace_refs=True)
#: Zenodo legacy deposit JSON serialzier version 1.0.0
githubjson_v1 = LegacyJSONSerializer(
    GitHubRecordSchemaV1, replace_refs=True)
#: Zenodo legacy deposit JSON serialzier version 1.0.0
deposit_legacyjson_v1 = DepositLegacyJSONSerializer(
    LegacyRecordSchemaV1, replace_refs=True)
#: MARCXML serializer version 1.0.0
marcxml_v1 = MARCXMLSerializer(
    to_marc21, schema_class=RecordSchemaMARC21, replace_refs=True)
#: BibTeX serializer version 1.0.0
bibtex_v1 = BibTeXSerializer()
#: DataCite serializer
datacite_v31 = DataCite31Serializer(DataCiteSchemaV1, replace_refs=True)
#: OAI DataCite serializer
oai_datacite = OAIDataCiteSerializer(
    v31=datacite_v31,
    datacentre='CERN.ZENODO',
)
#: Dublin Core serializer
dc_v1 = DublinCoreSerializer(DublinCoreV1, replace_refs=True)
#: CSL-JSON serializer
csl_v1 = JSONSerializer(RecordSchemaCSLJSON, replace_refs=True)
#: CSL Citation Formatter serializer
citeproc_v1 = CiteprocSerializer(csl_v1)


# Records-REST serializers
# ========================
#: JSON record serializer for individual records.
json_v1_response = record_responsify(json_v1, 'application/json')
#: JSON record legacy serializer for individual records.
legacyjson_v1_response = record_responsify(legacyjson_v1, 'application/json')
#: MARCXML record serializer for individual records.
marcxml_v1_response = record_responsify(marcxml_v1, 'application/marcxml+xml')
#: BibTeX record serializer for individual records.
bibtex_v1_response = record_responsify(bibtex_v1, 'application/x-bibtex')
#: DataCite v3.1 record serializer for individual records.
datacite_v31_response = record_responsify(
    datacite_v31, 'application/x-datacite+xml')
#: DublinCore record serializer for individual records.
dc_v1_response = record_responsify(dc_v1, 'application/x-dc+xml')
#: CSL-JSON record serializer for individual records.
csl_v1_response = record_responsify(
    csl_v1, 'application/vnd.citationstyles.csl+json')
#: CSL Citation Formatter serializer for individual records.
citeproc_v1_response = record_responsify(citeproc_v1, 'text/x-bibliography')


#: JSON record serializer for search results.
json_v1_search = search_responsify(json_v1, 'application/json')
#: JSON record legacy serializer for search results.
legacyjson_v1_search = search_responsify(legacyjson_v1, 'application/json')
#: MARCXML record serializer for search records.
marcxml_v1_search = search_responsify(marcxml_v1, 'application/marcxml+xml')
#: BibTeX serializer for search records.
bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
#: DataCite v3.1 record serializer for search records.
datacite_v31_search = search_responsify(
    datacite_v31, 'application/x-datacite+xml')
#: DublinCore record serializer for search records.
dc_v1_search = search_responsify(dc_v1, 'application/x-dc+xml')

# Deposit serializers
# ===================
#: JSON record legacy serializer for individual deposits.
deposit_legacyjson_v1_response = record_responsify(
    deposit_legacyjson_v1, 'application/json')
#: JSON record legacy serializer for deposit search results.
deposit_legacyjson_v1_search = search_responsify(
    deposit_legacyjson_v1, 'application/json')
#: JSON files legacy serializer for deposit files.
deposit_legacyjson_v1_files_response = files_responsify(
    FileSchemaV1, 'application/json')
#: JSON record serializer for individual records.
deposit_json_v1_response = record_responsify(
    deposit_json_v1, 'application/json')
#: JSON record serializer for search results.
deposit_json_v1_search = search_responsify(
    deposit_json_v1, 'application/json')

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
