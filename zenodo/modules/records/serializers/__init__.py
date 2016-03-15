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
from invenio_records_rest.serializers.json import JSONSerializer
from invenio_records_rest.serializers.response import record_responsify, \
    search_responsify

from .schemas.json import RecordSchemaJSONV1
from .schemas.marcxml import RecordSchemaMARC

json_v1 = JSONSerializer(RecordSchemaJSONV1)
marcxml_v1 = MARCXMLSerializer(to_marc21, schema_class=RecordSchemaMARC)
# datacite_v1 = None
# bibtex_v1 = None

json_v1_response = record_responsify(json_v1, 'application/json')
marcxml_v1_response = record_responsify(marcxml_v1, 'application/marc+xml')
# datacite_v1_response = record_responsify(
#    datacite_v1, 'application/x-datacite+xml')
# bibtex_v1_response = record_responsify(bibtex_v1, 'application/x-bibtex')

json_v1_search = search_responsify(json_v1, 'application/json')
marcxml_v1_search = search_responsify(marcxml_v1, 'application/marc+xml')
# datacite_v1_search = search_responsify(
#     datacite_v1, 'application/x-datacite+xml')
# bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
