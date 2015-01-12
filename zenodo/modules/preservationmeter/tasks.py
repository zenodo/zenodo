## -*- coding: utf-8 -*-
##
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


"""PreservationMeter tasks for Zenodo."""

from __future__ import absolute_import

from flask import current_app
from invenio.modules.records.api import get_record
from invenio.legacy.bibupload.utils import bibupload_record
from invenio.celery import celery

from .api import calculate_score


@celery.task(ignore_result=True)
def calculate_preservation_score(recid):
    """Calculate the preservation score of a given record."""
    r = get_record(recid)
    files = r[current_app.config['PRESERVATIONMETER_FILES_FIELD']]
    score = calculate_score(
        [(f['full_name'], f['path']) for f in files]
    )

    marcxml = """<record>
    <controlfield tag="001">{0}</controlfield>
    <datafield tag="347" ind1="" ind2="">
        <subfield code="p">{1}</subfield>
    </datafield>
    </record>
    """.format(recid, score)

    bibupload_record(marcxml)
