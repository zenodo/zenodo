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

"""Zenodo CSL-JSON schema."""

from __future__ import absolute_import, print_function

import re

from invenio_formatter.filters.datetime import from_isodate
from marshmallow import Schema, fields, missing

from zenodo.modules.records.models import ObjectType


class AuthorSchema(Schema):
    """Schema for an author."""

    family = fields.Method('get_family_name')
    given = fields.Method('get_given_names')

    def get_family_name(self, obj):
        """Get family name."""
        if {'familyname', 'givennames'} <= set(obj):
            return obj.get('familyname')
        else:
            return obj['name']

    def get_given_names(self, obj):
        """Get given names."""
        if {'familyname', 'givennames'} <= set(obj):
            return obj.get('givennames')
        return missing


class RecordSchemaCSLJSON(Schema):
    """Schema for records in CSL-JSON."""

    id = fields.Str(attribute='pid.pid_value')
    type = fields.Method('get_type')
    title = fields.Str(attribute='metadata.title')
    abstract = fields.Str(attribute='metadata.description')
    author = fields.List(fields.Nested(AuthorSchema),
                         attribute='metadata.creators')
    issued = fields.Method('get_issue_date')
    language = fields.Str(attribute='metadata.language')
    version = fields.Str(attribute='metadata.version')
    note = fields.Str(attribute='metadata.notes')

    DOI = fields.Str(attribute='metadata.doi')
    ISBN = fields.Str(attribute='metadata.imprint.isbn')
    ISSN = fields.Method('get_issn')

    container_title = fields.Method('get_container_title')
    page = fields.Method('get_pages')
    volume = fields.Str(attribute='metadata.journal.volume')
    issue = fields.Str(attribute='metadata.journal.issue')

    publisher = fields.Method('get_publisher')
    publisher_place = fields.Str(attribute='metadata.imprint.place')

    def get_journal_or_part_of(self, obj, key):
        """Get journal or part of."""
        m = obj['metadata']
        journal = m.get('journal', {}).get(key)
        part_of = m.get('part_of', {}).get(key)

        return journal or part_of or missing

    def get_container_title(self, obj):
        """Get container title."""
        return self.get_journal_or_part_of(obj, 'title')

    def get_pages(self, obj):
        """Get pages."""
        # Remove multiple dashes between page numbers (eg. 12--15)
        pages = self.get_journal_or_part_of(obj, 'pages')
        pages = re.sub('-+', '-', pages) if pages else pages
        return pages

    def get_publisher(self, obj):
        """Get publisher."""
        m = obj['metadata']
        publisher = m.get('imprint', {}).get('publisher')
        if publisher:
            return publisher

        if m.get('doi', '').startswith('10.5281/'):
            return 'Zenodo'

        return missing

    def get_type(self, obj):
        """Get record CSL type."""
        metadata = obj['metadata']
        obj_type = ObjectType.get_by_dict(metadata.get('resource_type'))
        return obj_type.get('csl', 'article') if obj_type else 'article'

    def get_issn(self, obj):
        """Get the record's ISSN."""
        for id in obj['metadata'].get('alternate_identifiers', []):
            if id['scheme'] == 'issn':
                return id['identifier']
        return missing

    def get_issue_date(self, obj):
        """Get a date in list format."""
        d = from_isodate(obj['metadata'].get('publication_date'))
        return {'date-parts': [[d.year, d.month, d.day]]} if d else missing
