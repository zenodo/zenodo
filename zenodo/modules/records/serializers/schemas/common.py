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

"""Definition of fields which are common between JSON and Legacy JSON."""

from __future__ import absolute_import, print_function

import arrow
import idutils
import jsonref
from flask import current_app, has_request_context, request, url_for
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from marshmallow import Schema, ValidationError, fields, post_dump, \
    post_load, pre_load, validate, validates, validates_schema
from six.moves.urllib.parse import quote
from werkzeug.routing import BuildError

from zenodo.modules.records.config import ZENODO_RELATION_TYPES
from zenodo.modules.records.models import AccessRight

from ...utils import is_deposit
from ..fields import DOI as DOIField
from ..fields import DateString, PersistentId, SanitizedHTML, TrimmedString


def clean_empty(data, keys):
    """Clean empty values."""
    for k in keys:
        if k in data and not data[k]:
            del data[k]
    return data


class StrictKeysMixin(object):
    """Ensure only defined keys exists in data."""

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        """Check for unknown keys."""
        if not isinstance(original_data, list):
            items = [original_data]
        else:
            items = original_data
        for original_data in items:
            for key in original_data:
                if key not in self.fields:
                    raise ValidationError(
                        'Unknown field name.'.format(key),
                        field_names=[key],
                    )


class RefResolverMixin(object):
    """Mixin for helping to validate if a JSONRef resolves."""

    def validate_jsonref(self, value):
        """Validate that a JSONRef resolves.

        Test is skipped if not explicitly requested and you are in an
        application context.
        """
        if not self.context.get('replace_refs') or not current_app:
            return True

        if not(isinstance(value, dict) and '$ref' in value):
            return True

        try:
            Record(value).replace_refs().dumps()
            return True
        except jsonref.JsonRefError:
            return False


class PersonSchemaV1(Schema, StrictKeysMixin):
    """Schema for a person."""

    name = TrimmedString(required=True)
    affiliation = TrimmedString()
    gnd = PersistentId(scheme='GND')
    orcid = PersistentId(scheme='ORCID')

    @post_dump(pass_many=False)
    def clean(self, data):
        """Clean empty values."""
        return clean_empty(data, ['orcid', 'gnd', 'affiliation'])

    @post_load(pass_many=False)
    def remove_gnd_prefix(self, data):
        """Remove GND prefix (which idutils normalization adds)."""
        gnd = data.get('gnd')
        if gnd and gnd.startswith('gnd:'):
            data['gnd'] = gnd[len('gnd:'):]

    @validates_schema
    def validate_data(self, data):
        """Validate schema."""
        name = data.get('name')
        if not name:
            raise ValidationError(
                _('Name is required.'),
                field_names=['name']
            )


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for a contributor."""

    type = fields.Str(required=True)

    @validates('type')
    def validate_type(self, value):
        """Validate the type."""
        if value not in \
                current_app.config['DEPOSIT_CONTRIBUTOR_DATACITE2MARC']:
            raise ValidationError(
                _('Invalid contributor type.'),
                field_names=['type']
            )


class IdentifierSchemaV1(Schema, StrictKeysMixin):
    """Schema for a identifiers.

    During deserialization the schema takes care of detecting the identifier
    scheme if not specified, as well as validating and normalizing the
    persistent identifier value.
    """

    identifier = PersistentId(required=True)
    scheme = fields.Str()

    @pre_load()
    def detect_scheme(self, data):
        """Load scheme."""
        id_ = data.get('identifier')
        scheme = data.get('scheme')
        if not scheme and id_:
            scheme = idutils.detect_identifier_schemes(id_)
            if scheme:
                data['scheme'] = scheme[0]
        return data

    @post_load()
    def normalize_identifier(self, data):
        """Normalize identifier."""
        data['identifier'] = idutils.normalize_pid(
            data['identifier'], data['scheme'])

    @validates_schema
    def validate_data(self, data):
        """Validate identifier and scheme."""
        id_ = data.get('identifier')
        scheme = data.get('scheme')
        if not id_:
            raise ValidationError(
                'Identifier is required.',
                field_names=['identifier']
            )

        schemes = idutils.detect_identifier_schemes(id_)
        if not schemes:
            raise ValidationError(
                'Not a valid persistent identifier.',
                field_names=['identifier']
            )
        if scheme not in schemes:
            raise ValidationError(
                'Not a valid {0} identifier.'.format(scheme),
                field_names=['identifier']
            )


class AlternateIdentifierSchemaV1(IdentifierSchemaV1):
    """Schema for a related identifier."""


class RelatedIdentifierSchemaV1(IdentifierSchemaV1):
    """Schema for a related identifier."""

    relation = fields.Str(
        required=True,
        validate=validate.OneOf(
            choices=[x[0] for x in ZENODO_RELATION_TYPES],
        )
    )


class SubjectSchemaV1(IdentifierSchemaV1):
    """Schema for a subject."""

    term = TrimmedString()


class CommonMetadataSchemaV1(Schema, StrictKeysMixin, RefResolverMixin):
    """Common metadata schema."""

    doi = DOIField()
    publication_date = DateString(required=True)
    title = TrimmedString(required=True, validate=validate.Length(min=3))
    creators = fields.Nested(
        PersonSchemaV1, many=True, validate=validate.Length(min=1))
    description = SanitizedHTML(
        required=True, validate=validate.Length(min=3))
    keywords = fields.List(TrimmedString())
    notes = TrimmedString()
    access_right = fields.Str(validate=validate.OneOf(
        choices=[
            AccessRight.OPEN,
            AccessRight.EMBARGOED,
            AccessRight.RESTRICTED,
            AccessRight.CLOSED,
        ],
    ))
    embargo_date = DateString()
    access_conditions = SanitizedHTML()
    subjects = fields.Nested(SubjectSchemaV1, many=True)
    contributors = fields.List(fields.Nested(ContributorSchemaV1))
    references = fields.List(TrimmedString(attribute='raw_reference'))
    related_identifiers = fields.Nested(RelatedIdentifierSchemaV1, many=True)
    alternate_identifiers = fields.Nested(
        AlternateIdentifierSchemaV1, many=True)

    @validates('embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )

    @validates('license')
    def validate_license_ref(self, value):
        """Validate if license resolves."""
        if not self.validate_jsonref(value):
            raise ValidationError(
                _('Invalid choice.'),
                field_names=['license'],
            )

    @validates('grants')
    def validate_grants_ref(self, values):
        """Validate if license resolves."""
        for v in values:
            if not self.validate_jsonref(v):
                raise ValidationError(
                    _('Invalid grant.'),
                    field_names=['grants'],
                )

    @validates('doi')
    def validate_doi(self, value):
        """Validate if doi exists."""
        if value and has_request_context():
            required_doi = self.context.get('required_doi')
            if value == required_doi:
                return
            try:
                PersistentIdentifier.get('doi', value)
                raise ValidationError(
                    _('DOI already exists in Zenodo.'),
                    field_names=['doi'])
            except PIDDoesNotExistError:
                pass

    @validates_schema()
    def validate_license(self, data):
        """Validate license."""
        acc = data.get('access_right')
        if acc in [AccessRight.OPEN, AccessRight.EMBARGOED] and \
                'license' not in data:
            raise ValidationError(
                _('Required when access right is open or embargoed.'),
                field_names=['license']
            )
        if acc == AccessRight.EMBARGOED and 'embargo_date' not in data:
            raise ValidationError(
                _('Required when access right is embargoed.'),
                field_names=['embargo_date']
            )
        if acc == AccessRight.RESTRICTED and 'access_conditions' not in data:
            raise ValidationError(
                _('Required when access right is restricted.'),
                field_names=['access_conditions']
            )

    @pre_load()
    def preload_accessrights(self, data):
        """Remove invalid access rights combinations."""
        # Default value
        if 'access_right' not in data:
            data['access_right'] = AccessRight.OPEN

        # Pop values which should not be set for a given access right.
        if data.get('access_right') not in [
                AccessRight.OPEN, AccessRight.EMBARGOED]:
            data.pop('license', None)
        if data.get('access_right') != AccessRight.RESTRICTED:
            data.pop('access_conditions', None)
        if data.get('access_right') != AccessRight.EMBARGOED:
            data.pop('embargo_date', None)

    @pre_load()
    def preload_publicationdate(self, data):
        """Default publication date."""
        if 'publication_date' not in data:
            data['publication_date'] = arrow.utcnow().date().isoformat()

    @post_load()
    def postload_keywords_filter(self, data):
        """Filter empty keywords."""
        if 'keywords' in data:
            data['keywords'] = [
                kw for kw in data['keywords'] if kw.strip()
            ]

    @post_load()
    def postload_references(self, data):
        """Filter empty references and wrap them."""
        if 'references' in data:
            data['references'] = [
                {'raw_reference': ref}
                for ref in data['references'] if ref.strip()
            ]


class CommonRecordSchemaV1(Schema, StrictKeysMixin):
    """Common record schema."""

    id = fields.Integer(attribute='pid.pid_value', dump_only=True)
    doi = fields.Str(attribute='metadata.doi', dump_only=True)
    links = fields.Method('dump_links', dump_only=True)
    created = fields.Str(dump_only=True)

    def dump_links(self, obj):
        """Dump links."""
        links = obj.get('links', {})
        m = obj.get('metadata', {})

        doi = m.get('doi')
        if current_app and doi:
            links['badge'] = "{base}/badge/doi/{value}.svg".format(
                base=current_app.config.get('THEME_SITEURL'),
                value=quote(doi),
            )
            links['doi'] = idutils.to_url(doi, 'doi')

        if has_request_context():
            if is_deposit(m):
                bucket_id = m.get('_buckets', {}).get('deposit')
                recid = m.get('recid') if m.get('_deposit', {}).get('pid') \
                    else None
                api_key = 'record'
                html_key = 'record_html'
            else:
                bucket_id = m.get('_buckets', {}).get('record')
                recid = m.get('recid')
                api_key = None
                html_key = 'html'

            if bucket_id:
                try:
                    links['bucket'] = url_for(
                        'invenio_files_rest.bucket_api',
                        bucket_id=bucket_id,
                        _external=True,
                    )
                except BuildError:
                    pass

            if recid:
                try:
                    if api_key:
                        links[api_key] = url_for(
                            'invenio_records_rest.recid_item',
                            pid_value=recid,
                            _external=True,
                        )
                    if html_key:
                        links[html_key] = \
                            current_app.config['RECORDS_UI_ENDPOINT'].format(
                            host=request.host,
                            scheme=request.scheme,
                            pid_value=recid,
                        )
                except BuildError:
                    pass

            return links

    @post_load(pass_many=False)
    def remove_envelope(self, data):
        """Post process data."""
        # Remove envelope
        if 'metadata' in data:
            data = data['metadata']

        # Record schema.
        data['$schema'] = \
            'https://zenodo.org/schemas/deposits/records/record-v1.0.0.json'

        return data
