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

"""Zenodo JSON schema."""

from __future__ import absolute_import, print_function

from dateutil.parser import parse
from marshmallow import Schema, fields

from zenodo.modules.records.models import AccessRight, ObjectType


class PersonSchemaV1(Schema):
    """Schema for a person."""

    name = fields.Str()
    affiliation = fields.Str()
    gnd = fields.Str()
    orcid = fields.Str()


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for a contributor."""

    type = fields.Str()


class RelatedIdentifierSchemav1(Schema):
    """Schema for a related identifier."""

    id = fields.Str()
    relation = fields.Str()
    scheme = fields.Str()


class JournalSchemaV1(Schema):
    """Schema for a journal."""

    title = fields.Str()
    volume = fields.Str()
    issue = fields.Str()
    pages = fields.Str()


class ConferenceSchemaV1(Schema):
    """Schema for a journal."""

    title = fields.Str()
    acronym = fields.Str()
    dates = fields.Str()
    place = fields.Str()
    url = fields.Str()
    session = fields.Str()
    session_part = fields.Str()


class SubjectSchemaV1(Schema):
    """Schema for a subject."""

    term = fields.Str()
    id = fields.Str()
    scheme = fields.Str()


class MetadataSchemaV1(Schema):
    """Schema for metadata."""

    type = fields.Str(attribute="upload_type.type")
    subtype = fields.Str(attribute="upload_type.subtype", missing=None)
    type_title = fields.Method('get_type_title')

    publication_date = fields.Str()
    doi = fields.Str(attribute='doi')

    creators = fields.List(fields.Nested(PersonSchemaV1), attribute='authors')
    contributors = fields.List(
        fields.Nested(ContributorSchemaV1), attribute='contributors')

    title = fields.Str()
    description = fields.Str()
    notes = fields.Str()
    keywords = fields.List(fields.Str)
    license = fields.Str(attribute="license.identifier")
    access_right = fields.Method('get_access_right')
    access_right_category = fields.Method('get_access_right_category')
    embargo_date = fields.Str()
    access_condition = fields.Str()

    related_identifiers = fields.List(fields.Nested(RelatedIdentifierSchemav1))
    subjects = fields.List(fields.Nested(SubjectSchemaV1))
    grants = fields.List(fields.Str)

    communities = fields.List(fields.Str)

    references = fields.List(fields.Str)
    journal = fields.Nested(JournalSchemaV1)
    conference = fields.Nested(ConferenceSchemaV1)

    def get_type_title(self, obj):
        """Get type title."""
        try:
            return ObjectType.get_by_dict(obj['upload_type'])['title']['en']
        except Exception:
            from flask import current_app
            current_app.logger.exception(
                "Failed object {}".format(obj['upload_type']))
            raise

    def get_access_right(self, obj):
        """Get access right information."""
        dt = obj.get('embargo_date')
        return AccessRight.get(
            obj['access_right'],
            embargo_date=parse(dt).date() if dt else None
        )

    def get_access_right_category(self, obj):
        """Get access right category."""
        return AccessRight.as_category(self.get_access_right(obj))


class RecordSchemaJSONV1(Schema):
    """Schema for records v1 in JSON."""

    id = fields.Integer(attribute='pid.pid_value')
    metadata = fields.Nested(MetadataSchemaV1)
    links = fields.Raw()
    created = fields.Str()
    updated = fields.Str()
    revision = fields.Integer()
