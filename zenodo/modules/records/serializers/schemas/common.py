# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

import arrow
import idutils
import jsonref
import pycountry
from flask import current_app, has_request_context
from flask_babelex import lazy_gettext as _
from invenio_iiif.previewer import previewable_extensions as thumbnail_exts
from invenio_iiif.utils import ui_iiif_image_url
from invenio_pidrelations.serializers.utils import serialize_relations
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from marshmallow import Schema, ValidationError, fields, missing, post_dump, \
    post_load, pre_dump, pre_load, validate, validates, validates_schema
from six.moves.urllib.parse import quote
from werkzeug.routing import BuildError

from zenodo.modules.records import current_custom_metadata
from zenodo.modules.records.config import ZENODO_RELATION_TYPES
from zenodo.modules.records.models import AccessRight

from ...utils import is_deposit, is_record
from ..fields import DOI as DOIField
from ..fields import DateString, PersistentId, SanitizedHTML, SanitizedUnicode


def clean_empty(data, keys):
    """Clean empty values."""
    for k in keys:
        if k in data and not data[k]:
            del data[k]
    return data


URLS = {
    'badge': '{base}/badge/doi/{doi}.svg',
    'bucket': '{base}/files/{bucket}',
    'funder': '{base}/funders/{id}',
    'grant': '{base}/grants/{id}',
    'object': '{base}/files/{bucket}/{key}',
    'deposit_html': '{base}/deposit/{id}',
    'deposit': '{base}/deposit/depositions/{id}',
    'record_html': '{base}/record/{id}',
    'record_file': '{base}/record/{id}/files/{filename}',
    'record': '{base}/records/{id}',
    'thumbnail': '{base}{path}',
    'thumbs': '{base}/record/{id}/thumb{size}',
    'community': '{base}/communities/{id}',
}


def link_for(base, tpl, **kwargs):
    """Create a link using specific template."""
    tpl = URLS.get(tpl)
    for k in ['key', ]:
        if k in kwargs:
            kwargs[k] = quote(kwargs[k].encode('utf8'))
    return tpl.format(base=base, **kwargs)


def api_link_for(tpl, **kwargs):
    """Create an API link using specific template."""
    is_api_app = 'invenio-deposit-rest' in current_app.extensions

    base = '{}/api'
    if current_app.testing and is_api_app:
        base = '{}'

    return link_for(
        base.format(current_app.config['THEME_SITEURL']), tpl, **kwargs)


def ui_link_for(tpl, **kwargs):
    """Create an UI link using specific template."""
    return link_for(current_app.config['THEME_SITEURL'], tpl, **kwargs)


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

    name = SanitizedUnicode(required=True)
    affiliation = SanitizedUnicode()
    gnd = PersistentId(scheme='GND')
    orcid = PersistentId(scheme='ORCID')

    @post_dump(pass_many=False)
    @post_load(pass_many=False)
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
    """Schema for an alternate identifier."""


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

    term = SanitizedUnicode()


class DateSchemaV1(Schema):
    """Schema for date intervals."""

    start = DateString()
    end = DateString()
    type = fields.Str(required=True)
    description = fields.Str()


class LocationSchemaV1(Schema):
    """Schema for geographical locations."""

    lat = fields.Float()
    lon = fields.Float()
    place = SanitizedUnicode(required=True)
    description = SanitizedUnicode()

    @validates('lat')
    def validate_latitude(self, value):
        """Validate that location exists."""
        if not (-90 <= value <= 90):
            raise ValidationError(
                _('Latitude must be between -90 and 90.')
            )

    @validates('lon')
    def validate_longitude(self, value):
        """Validate that location exists."""
        if not (-180 <= value <= 180):
            raise ValidationError(
                _('Longitude must be between -180 and 180.')
            )


class CommonMetadataSchemaV1(Schema, StrictKeysMixin, RefResolverMixin):
    """Common metadata schema."""

    doi = DOIField(missing='')
    publication_date = DateString(required=True)
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    creators = fields.Nested(
        PersonSchemaV1, many=True, validate=validate.Length(min=1))
    dates = fields.List(
        fields.Nested(DateSchemaV1), validate=validate.Length(min=1))
    description = SanitizedHTML(
        required=True, validate=validate.Length(min=3))
    keywords = fields.List(SanitizedUnicode())
    locations = fields.List(
        fields.Nested(LocationSchemaV1), validate=validate.Length(min=1))
    notes = SanitizedHTML()
    version = SanitizedUnicode()
    language = SanitizedUnicode()
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
    references = fields.List(SanitizedUnicode(attribute='raw_reference'))
    related_identifiers = fields.Nested(
        RelatedIdentifierSchemaV1, many=True)
    alternate_identifiers = fields.Nested(
        AlternateIdentifierSchemaV1, many=True)
    method = SanitizedUnicode()

    @validates('locations')
    def validate_locations(self, value):
        """Validate that there should be both latitude and longitude."""
        for location in value:
            if (location.get('lon') and not location.get('lat')) or \
                (location.get('lat') and not location.get('lon')):
                raise ValidationError(
                    _('There should be both latitude and longitude.'),
                    field_names=['locations'])

    @validates('language')
    def validate_language(self, value):
        """Validate that language is ISO 639-3 value."""
        if not pycountry.languages.get(alpha_3=value):
            raise ValidationError(
                _('Language must be a lower-cased 3-letter ISO 639-3 string.'),
                field_name=['language']
            )

    @validates('dates')
    def validate_dates(self, value):
        """Validate that start date is before the corresponding end date."""
        for interval in value:
            start = arrow.get(interval.get('start'), 'YYYY-MM-DD').date() \
                if interval.get('start') else None
            end = arrow.get(interval.get('end'), 'YYYY-MM-DD').date() \
                if interval.get('end') else None

            if not start and not end:
                raise ValidationError(
                    _('There must be at least one date.'),
                    field_names=['dates']
                )
            if start and end and start > end:
                raise ValidationError(
                    _('"start" date must be before "end" date.'),
                    field_names=['dates']
                )

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

            err = ValidationError(_('DOI already exists in Zenodo.'),
                                  field_names=['doi'])

            try:
                doi_pid = PersistentIdentifier.get('doi', value)
            except PIDDoesNotExistError:
                return

            # If the DOI exists, check if it's been assigned to this record
            # by fetching the recid and comparing both PIDs record UUID
            try:
                recid_pid = PersistentIdentifier.get(
                    'recid', self.context['recid'])
            except PIDDoesNotExistError:
                # There's no way to verify if this DOI belongs to this record
                raise err

            doi_uuid = doi_pid.get_assigned_object()
            recid_uuid = recid_pid.get_assigned_object()

            if doi_uuid and doi_uuid == recid_uuid:
                return
            else:  # DOI exists and belongs to a different record
                raise err

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

    custom = fields.Method('dump_custom', 'load_custom')

    def load_custom(self, obj):
        """Validate the custom metadata according to config."""
        if not obj:
            return missing

        if not isinstance(obj, dict):
            raise ValidationError('Not an object.', field_names=['custom'])

        valid_vocabulary = current_custom_metadata.available_vocabulary_set
        term_types = current_custom_metadata.term_types
        valid_terms = current_custom_metadata.terms
        for term, values in obj.items():
            if term not in valid_vocabulary:
                raise ValidationError(
                    'Zenodo does not support "{0}" as a custom metadata term.'
                    .format(term),
                    field_names=['custom'])

            # Validate term type
            term_type = term_types[valid_terms[term]['term_type']]
            if not isinstance(values, list):
                raise ValidationError(
                        'Term "{0}" should be of type array.'
                        .format(term),
                        field_names=['custom'])
            if len(values) == 0:
                raise ValidationError(
                        'No values were provided for term "{0}".'
                        .format(term),
                        field_names=['custom'])
            for value in values:
                if not isinstance(value, term_type):
                    raise ValidationError(
                        'Invalid type for term "{0}", should be "{1}".'
                        .format(term, valid_terms[term]['term_type']),
                        field_names=['custom'])
        return obj

    def dump_custom(self, data):
        """Dump custom metadata."""
        return data.get('custom', missing)

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
    conceptrecid = SanitizedUnicode(
        attribute='metadata.conceptrecid', dump_only=True)
    doi = SanitizedUnicode(attribute='metadata.doi', dump_only=True)
    conceptdoi = SanitizedUnicode(
        attribute='metadata.conceptdoi', dump_only=True)

    links = fields.Method('dump_links', dump_only=True)
    created = fields.Str(dump_only=True)

    @pre_dump()
    def predump_relations(self, obj):
        """Add relations to the schema context."""
        m = obj.get('metadata', {})
        if 'relations' not in m:
            pid = self.context['pid']
            # For deposits serialize the record's relations
            if is_deposit(m):
                pid = PersistentIdentifier.get('recid', m['recid'])
            m['relations'] = serialize_relations(pid)

        # Remove some non-public fields
        if is_record(m):
            version_info = m['relations'].get('version', [])
            if version_info:
                version_info[0].pop('draft_child_deposit', None)

    def dump_links(self, obj):
        """Dump links."""
        links = obj.get('links', {})
        if current_app:
            links.update(self._dump_common_links(obj))

        try:
            m = obj.get('metadata', {})
            if is_deposit(m):
                links.update(self._dump_deposit_links(obj))
            else:
                links.update(self._dump_record_links(obj))
        except BuildError:
            pass
        return links

    def _thumbnail_url(self, fileobj, thumbnail_size):
        """Create the thumbnail URL for an image."""
        return link_for(
            current_app.config.get('THEME_SITEURL'),
            'thumbnail',
            path=ui_iiif_image_url(
                fileobj,
                size='{},'.format(thumbnail_size),
                image_format='png' if fileobj['type'] == 'png' else 'jpg',
            )
        )

    def _thumbnail_urls(self, recid):
        """Create the thumbnail URL for an image."""
        thumbnail_urls = {}
        cached_sizes = current_app.config.get('CACHED_THUMBNAILS')
        for size in cached_sizes:
            thumbnail_urls[size] = link_for(
                current_app.config.get('THEME_SITEURL'),
                'thumbs',
                id=recid,
                size=size
            )
        return thumbnail_urls

    def _dump_common_links(self, obj):
        """Dump common links for deposits and records."""
        links = {}
        m = obj.get('metadata', {})

        doi = m.get('doi')
        if doi:
            links['badge'] = ui_link_for('badge', doi=quote(doi))
            links['doi'] = idutils.to_url(doi, 'doi', 'https')

        conceptdoi = m.get('conceptdoi')
        if conceptdoi:
            links['conceptbadge'] = ui_link_for('badge', doi=quote(conceptdoi))
            links['conceptdoi'] = idutils.to_url(conceptdoi, 'doi', 'https')

        files = m.get('_files', [])
        for f in files:
            if f.get('type') in thumbnail_exts:
                try:
                    # First previewable image is used for preview.
                    links['thumbs'] = self._thumbnail_urls(m.get('recid'))
                    links['thumb250'] = self._thumbnail_url(f, 250)
                except RuntimeError:
                    pass
                break

        return links

    def _dump_record_links(self, obj):
        """Dump record-only links."""
        links = {}
        m = obj.get('metadata')
        bucket_id = m.get('_buckets', {}).get('record')
        recid = m.get('recid')

        if bucket_id:
            links['bucket'] = api_link_for('bucket', bucket=bucket_id)

        links['html'] = ui_link_for('record_html', id=recid)

        # Generate relation links
        links.update(self._dump_relation_links(m))
        return links

    def _dump_deposit_links(self, obj):
        """Dump deposit-only links."""
        links = {}
        m = obj.get('metadata')
        bucket_id = m.get('_buckets', {}).get('deposit')
        recid = m.get('recid')
        is_published = 'pid' in m.get('_deposit', {})

        if bucket_id:
            links['bucket'] = api_link_for('bucket', bucket=bucket_id)

        # Record links
        if is_published:
            links['record'] = api_link_for('record', id=recid)
            links['record_html'] = ui_link_for('record_html', id=recid)

        # Generate relation links
        links.update(self._dump_relation_links(m))
        return links

    def _dump_relation_links(self, metadata):
        """Dump PID relation links."""
        links = {}
        relations = metadata.get('relations')
        if relations:
            version_info = next(iter(relations.get('version', [])), None)
            if version_info:
                last_child = version_info.get('last_child')
                if last_child:
                    links['latest'] = api_link_for(
                        'record', id=last_child['pid_value'])
                    links['latest_html'] = ui_link_for(
                        'record_html', id=last_child['pid_value'])

                if is_deposit(metadata):
                    draft_child_depid = version_info.get('draft_child_deposit')
                    if draft_child_depid:
                        links['latest_draft'] = api_link_for(
                            'deposit', id=draft_child_depid['pid_value'])
                        links['latest_draft_html'] = ui_link_for(
                            'deposit_html', id=draft_child_depid['pid_value'])
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
