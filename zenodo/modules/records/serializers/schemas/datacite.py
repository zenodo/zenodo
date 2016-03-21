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

from marshmallow import Schema, fields


class IdentifierSchema(Schema):
    """Identifier schema."""

    identifier = fields.Str(attribute='doi')
    identifierType = fields.Constant('DOI')


class CreatorSchema(Schema):
    """Creator schema."""

    creatorName = fields.Str(attribute='name')
    affiliation = fields.Str()
    # TODO Support for ORCID/GND


class TitleSchema(Schema):
    """Title schema."""

    title = fields.Str(attribute='title')


class DateSchema(Schema):
    """Date schema."""

    date = fields.Str(attribute='date')
    dateType = fields.Str(attribute='type')


class DataCiteSchemaJSONV1(Schema):
    """Schema for records v1 in JSON."""

    identifier = fields.Nested(IdentifierSchema, attribute='metadata')
    creators = fields.List(
        fields.Nested(CreatorSchema),
        attribute='metadata.authors')
    titles = fields.List(
        fields.Nested(TitleSchema),
        attribute='metadata.title')
    publisher = fields.Constant('Zenodo')
    # TODO: Fix date -> year only
    publicationYear = fields.Str(attribute='metadata.publication_date')
    # TODO: Subjects from both keywords and subjects
    # TOOD: Contributors
    dates = fields.Method('get_dates')

    def get_dates(self, obj):
        """Get dates."""
        s = DateSchema()

        if obj.get('embargo_date'):
            return [
                s.dump(dict(
                    date=obj['metadata']['embargo_date'],
                    type='Available')).data,
                s.dump(dict(
                    date=obj['metadata']['publication_date'],
                    type='Accepted')).data,
            ]
        else:
            return [s.dump(dict(
                date=obj['metadata']['publication_date'],
                type='Issued')).data, ]
