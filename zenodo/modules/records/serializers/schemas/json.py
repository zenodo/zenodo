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

from datetime import datetime

from flask import url_for
from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, missing, post_load, \
    validate, validates_schema
from werkzeug.routing import BuildError

from .. import fields as zfields
from ...models import AccessRight, ObjectType


class ResourceTypeSchema(Schema):
    """Resource type schema."""

    type = fields.Str(
        required=True,
        error_messages=dict(
            required=_('Type must be specified.')
        ),
    )
    subtype = fields.Str()
    title = fields.Method('get_title', dump_only=True)

    def get_title(self, obj):
        """Get title."""
        obj = ObjectType.get_by_dict(obj)
        return obj['title']['en'] if obj else missing

    @validates_schema
    def validate_data(self, data):
        """Validate resource type."""
        obj = ObjectType.get_by_dict(data)
        if obj is None:
            raise ValidationError(_('Invalid resource type.'))


class IdentifierSchemaV1(Schema):
    """Schema for a identifiers."""

    identifier = zfields.PersistentId()
    scheme = fields.Str()


class RelatedIdentifierSchemaV1(IdentifierSchemaV1):
    """Schema for a related identifier."""

    relation = fields.Str()


class AlternateIdentifierSchemaV1(IdentifierSchemaV1):
    """Schema for a related identifier."""


class SubjectSchemaV1(IdentifierSchemaV1):
    """Schema for a subject."""

    term = fields.Str()


class PersonSchemaV1(Schema):
    """Schema for a person."""

    name = fields.Str()
    affiliation = fields.Str()
    gnd = zfields.PersistentId(scheme='GND')
    orcid = zfields.PersistentId(scheme='ORCID')


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for a contributor."""

    type = fields.Str()


class JournalSchemaV1(Schema):
    """Schema for a journal."""

    issue = fields.Str()
    pages = fields.Str()
    title = fields.Str()
    volume = fields.Str()
    year = fields.Str()


class MeetingSchemaV1(Schema):
    """Schema for a meeting."""

    title = fields.Str()
    acronym = fields.Str()
    dates = fields.Str()
    place = fields.Str()
    url = fields.Str()
    session = fields.Str()
    session_part = fields.Str()


class ImprintSchemaV1(Schema):
    """Schema for imprint."""

    publisher = fields.Str()
    place = fields.Str()


class PartOfSchemaV1(Schema):
    """Schema for imprint."""

    pages = fields.Str()
    place = fields.Str()
    publisher = fields.Str()
    title = fields.Str()
    year = fields.Str()
    isbn = fields.Str()


class ThesisSchemaV1(Schema):
    """Schema for thesis."""

    university = fields.Str()
    supervisors = fields.Nested(PersonSchemaV1, many=True)


class FunderSchemaV1(Schema):
    """Schema for a funder."""

    doi = fields.Str()
    name = fields.Str(dump_only=True)
    acronyms = fields.List(fields.Str(), dump_only=True)
    links = fields.Method('get_funder_url', dump_only=True)

    def get_funder_url(self, obj):
        """Get grant url."""
        try:
            return dict(self=url_for(
                'invenio_records_rest.frdoi_item',
                pid_value=obj['doi'],
                _external=True
            ))
        except BuildError:
            return missing


class GrantSchemaV1(Schema):
    """Schema for a grant."""

    title = fields.Str(dump_only=True)
    code = fields.Str()
    program = fields.Str(dump_only=True)
    acronym = fields.Str(dump_only=True)
    funder = fields.Nested(FunderSchemaV1)
    links = fields.Method('get_grant_url', dump_only=True)

    def get_grant_url(self, obj):
        """Get grant url."""
        try:
            return dict(self=url_for(
                'invenio_records_rest.grant_item',
                pid_value=obj['internal_id'],
                _external=True
            ))
        except BuildError:
            return missing


class ActionSchemaV1(Schema):
    """Schema for a actions."""

    prereserve_doi = fields.Str(load_only=True)


class MetadataSchemaV1(Schema):
    """Schema for a record."""

    doi = zfields.DOI()
    resource_type = fields.Nested(ResourceTypeSchema)
    publication_date = fields.Date(
        default=datetime.utcnow().date()
    )
    title = zfields.TrimmedString(
        required=True,
        validate=validate.Length(min=3),
    )
    creators = fields.Nested(PersonSchemaV1, many=True)
    description = zfields.TrimmedString(
        validate=validate.Length(min=3),
    )
    keywords = fields.List(zfields.TrimmedString)
    subjects = fields.Nested(SubjectSchemaV1, many=True)
    notes = zfields.TrimmedString()
    access_right = fields.Str()
    access_right_category = fields.Method(
        'get_access_right_category', dump_only=True)
    embargo_date = fields.Date()
    access_conditions = fields.Str()
    # TODO
    license = fields.Str(attribute="license.identifier")
    # TODO
    communities = fields.List(fields.Str)
    grants = fields.Nested(GrantSchemaV1, many=True)
    related_identifiers = fields.Nested(RelatedIdentifierSchemaV1, many=True)
    alternate_identifiers = fields.Nested(
        AlternateIdentifierSchemaV1, many=True)
    contributors = fields.Nested(ContributorSchemaV1, many=True)
    references = fields.List(fields.Str, attribute='references.raw_reference')
    journal = fields.Nested(JournalSchemaV1)
    meeting = fields.Nested(MeetingSchemaV1)
    part_of = fields.Nested(PartOfSchemaV1)
    imprint = fields.Nested(ImprintSchemaV1)
    thesis = fields.Nested(ThesisSchemaV1)

    def get_access_right_category(self, obj):
        """Get access right category."""
        return AccessRight.as_category(obj.get('access_right'))

    @post_load(pass_many=False)
    def format_dates(self, data):
        """Convert dates back to to ISO-format."""
        print(data)
        print('Stop it')
        for f in ['publication_date', 'embargo_date']:
            if f in data:
                data[f] = data[f].isoformat()


class RecordSchemaJSONV1(Schema):
    """Schema for records v1 in JSON."""

    id = fields.Integer(attribute='pid.pid_value', dump_only=True)
    owners = fields.List(
        fields.Integer, attribute='metadata.owners', dump_only=True)
    metadata = fields.Nested(MetadataSchemaV1)
    links = fields.Raw(dump_only=True)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)
    _deposit_actions = fields.Nested(
        ActionSchemaV1, load_from='actions', dump_to='actions')

    @post_load(pass_many=False)
    def remove_envelope(self, data):
        """Post process data."""
        # Remove envelope
        data['metadata']['_deposit_actions'] = data['_deposit_actions']
        data = data['metadata']

        # Record schema.
        data['$schema'] = \
            'https://zenodo.org/schemas/deposits/records/record-v1.0.0.json'

        return data
