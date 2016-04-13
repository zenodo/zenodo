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

"""Cerberus schemas for Zenodo legacy JSON."""

from __future__ import absolute_import, print_function

metadata_schema = {
    'schema': {
        'access_conditions': {'type': 'any'},
        'access_right': {'type': 'any'},
        'communities': {'type': 'list'},
        'conference_acronym': {'type': 'any'},
        'conference_dates': {'type': 'any'},
        'conference_place': {'type': 'any'},
        'conference_session': {'type': 'any'},
        'conference_session_part': {'type': 'any'},
        'conference_title': {'type': 'any'},
        'conference_url': {'type': 'any'},
        'contributors': {'type': 'list'},
        'creators': {'type': 'list'},
        'description': {'type': 'any'},
        'doi': {'type': 'any'},
        'embargo_date': {'type': 'any'},
        'grants': {'type': 'list'},
        'image_type': {'type': 'any'},
        'imprint_isbn': {'type': 'any'},
        'imprint_place': {'type': 'any'},
        'imprint_publisher': {'type': 'any'},
        'journal_issue': {'type': 'any'},
        'journal_pages': {'type': 'any'},
        'journal_title': {'type': 'any'},
        'journal_volume': {'type': 'any'},
        'keywords': {'type': 'list'},
        'license': {'type': 'any'},
        'notes': {'type': 'any'},
        'partof_pages': {'type': 'any'},
        'partof_title': {'type': 'any'},
        'prereserve_doi': {'type': 'any'},
        'publication_date': {'type': 'any'},
        'publication_type': {'type': 'any'},
        'references': {'type': 'any'},
        'related_identifiers': {'type': 'list'},
        'subjects': {'type': 'list'},
        'thesis_supervisors': {'type': 'list'},
        'thesis_university': {'type': 'any'},
        'title': {'type': 'any'},
        'upload_type': {'type': 'any'}},
    'type': 'dict'
}

deposit_schema = {
    'metadata': metadata_schema,
}
