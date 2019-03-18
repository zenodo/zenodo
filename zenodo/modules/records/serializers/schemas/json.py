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

from __future__ import absolute_import, print_function, unicode_literals

from flask_babelex import lazy_gettext as _
from invenio_pidrelations.serializers.utils import serialize_relations
from invenio_pidstore.models import PersistentIdentifier
from marshmallow import Schema, ValidationError, fields, missing, \
    validates_schema
from werkzeug.routing import BuildError

from zenodo.modules.records.utils import is_deposit
from zenodo.modules.stats.utils import get_record_stats

from ...models import AccessRight, ObjectType
from . import common


class StrictKeysSchema(Schema):
    """Ensure only valid keys exists."""

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        """Check for unknown keys."""
        for key in original_data:
            if key not in self.fields:
                raise ValidationError('Unknown field name {}'.format(key))


class ResourceTypeSchema(StrictKeysSchema):
    """Resource type schema."""

    type = fields.Str(
        required=True,
        error_messages=dict(
            required=_('Type must be specified.')
        ),
    )
    subtype = fields.Str()
    openaire_subtype = fields.Str()
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

    def dump_openaire_type(self, obj):
        """Get OpenAIRE subtype."""
        acc = obj.get('access_right')
        if acc:
            return AccessRight.as_category(acc)
        return missing


class JournalSchemaV1(StrictKeysSchema):
    """Schema for a journal."""

    issue = fields.Str()
    pages = fields.Str()
    title = fields.Str()
    volume = fields.Str()
    year = fields.Str()


class MeetingSchemaV1(StrictKeysSchema):
    """Schema for a meeting."""

    title = fields.Str()
    acronym = fields.Str()
    dates = fields.Str()
    place = fields.Str()
    url = fields.Str()
    session = fields.Str()
    session_part = fields.Str()


class ImprintSchemaV1(StrictKeysSchema):
    """Schema for imprint."""

    publisher = fields.Str()
    place = fields.Str()
    isbn = fields.Str()


class PartOfSchemaV1(StrictKeysSchema):
    """Schema for imprint."""

    pages = fields.Str()
    title = fields.Str()


class ThesisSchemaV1(StrictKeysSchema):
    """Schema for thesis."""

    university = fields.Str()
    supervisors = fields.Nested(common.PersonSchemaV1, many=True)


class FunderSchemaV1(StrictKeysSchema):
    """Schema for a funder."""

    doi = fields.Str()
    name = fields.Str(dump_only=True)
    acronyms = fields.List(fields.Str(), dump_only=True)
    links = fields.Method('get_funder_url', dump_only=True)

    def get_funder_url(self, obj):
        """Get grant url."""
        return dict(self=common.api_link_for('funder', id=obj['doi']))


class GrantSchemaV1(StrictKeysSchema):
    """Schema for a grant."""

    title = fields.Str(dump_only=True)
    code = fields.Str()
    program = fields.Str(dump_only=True)
    acronym = fields.Str(dump_only=True)
    funder = fields.Nested(FunderSchemaV1)
    links = fields.Method('get_grant_url', dump_only=True)

    def get_grant_url(self, obj):
        """Get grant url."""
        return dict(self=common.api_link_for('grant', id=obj['internal_id']))


class CommunitiesSchemaV1(StrictKeysSchema):
    """Schema for communities."""

    id = fields.Function(lambda x: x)


class ActionSchemaV1(StrictKeysSchema):
    """Schema for a actions."""

    prereserve_doi = fields.Str(load_only=True)


class FilesSchema(Schema):
    """Files metadata schema."""

    type = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    bucket = fields.String()
    key = fields.String()
    links = fields.Method('get_links')

    def get_links(self, obj):
        """Get links."""
        return {
            'self': common.api_link_for(
                'object', bucket=obj['bucket'], key=obj['key'])
        }


class OwnerSchema(StrictKeysSchema):
    """Schema for owners.

    Allows us to later introduce more properties for an owner.
    """

    id = fields.Function(lambda x: x)


class LicenseSchemaV1(StrictKeysSchema):
    """Schema for license.

    Allows us to later introduce more properties for an owner.
    """

    id = fields.Str(attribute='id')


class MetadataSchemaV1(common.CommonMetadataSchemaV1):
    """Schema for a record."""

    resource_type = fields.Nested(ResourceTypeSchema)
    access_right_category = fields.Method(
        'dump_access_right_category', dump_only=True)
    license = fields.Nested(LicenseSchemaV1)
    communities = fields.Nested(CommunitiesSchemaV1, many=True)
    grants = fields.Nested(GrantSchemaV1, many=True)
    journal = fields.Nested(JournalSchemaV1)
    meeting = fields.Nested(MeetingSchemaV1)
    imprint = fields.Nested(ImprintSchemaV1)
    part_of = fields.Nested(PartOfSchemaV1)
    thesis = fields.Nested(ThesisSchemaV1)
    relations = fields.Method('dump_relations')

    def dump_access_right_category(self, obj):
        """Get access right category."""
        acc = obj.get('access_right')
        if acc:
            return AccessRight.as_category(acc)
        return missing

    def dump_relations(self, obj):
        """Dump the relations to a dictionary."""
        if 'relations' in obj:
            return obj['relations']
        if is_deposit(obj):
            pid = self.context['pid']
            return serialize_relations(pid)
        else:
            pid = self.context['pid']
            return serialize_relations(pid)


class RecordSchemaV1(common.CommonRecordSchemaV1):
    """Schema for records v1 in JSON."""

    files = fields.Nested(
        FilesSchema, many=True, dump_only=True, attribute='files')
    metadata = fields.Nested(MetadataSchemaV1)
    owners = fields.List(
        fields.Integer, attribute='metadata.owners', dump_only=True)
    revision = fields.Integer(dump_only=True)
    updated = fields.Str(dump_only=True)

    stats = fields.Method('dump_stats')

    def dump_stats(self, obj):
        """Dump the stats to a dictionary."""
        if '_stats' in obj.get('metadata', {}):
            return obj['metadata'].get('_stats', {})
        else:
            pid = self.context.get('pid')
            if isinstance(pid, PersistentIdentifier):
                return get_record_stats(pid.object_uuid, False)
            else:
                return None


class DepositSchemaV1(RecordSchemaV1):
    """Deposit schema.

    Same as the Record schema except for some few extra additions.
    """

    files = None
    owners = fields.Nested(
        OwnerSchema, dump_only=True, attribute='metadata._deposit.owners',
        many=True)
    status = fields.Str(dump_only=True, attribute='metadata._deposit.status')
    recid = fields.Str(dump_only=True, attribute='metadata.recid')
