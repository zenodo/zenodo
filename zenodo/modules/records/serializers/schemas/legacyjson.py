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

"""Zenodo legacy JSON schema."""

import six
from flask import current_app
from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, missing, post_load, \
    pre_dump, pre_load, validate, validates, validates_schema

from zenodo.modules.records.models import ObjectType

from . import common
from ...minters import doi_generator
from ..fields import DOILink, PersistentId, TrimmedString


class FileSchemaV1(Schema):
    """Schema for files depositions."""

    id = fields.String(dump_only=True)
    filename = fields.String(attribute='key', dump_only=True)
    filesize = fields.Integer(attribute='size', dump_only=True)
    checksum = fields.Method('dump_checksum', dump_only=True)

    def dump_checksum(self, obj):
        """Dump checksum."""
        if 'checksum' not in obj:
            return missing
        algo, hashval = obj['checksum'].split(':')
        if algo != 'md5':
            return missing
        return hashval


class SubjectSchemaV1(common.SubjectSchemaV1):
    """Allow reading identifier from 'id' and 'identifier'."""

    identifier = PersistentId(required=True, dump_to='id', load_from='id')


class LegacyMetadataSchemaV1(common.CommonMetadataSchemaV1):
    """Legacy JSON metadata."""

    upload_type = fields.String(
        attribute='resource_type.type',
        required=True,
        validate=validate.OneOf(choices=ObjectType.get_types()),
    )
    publication_type = fields.Method(
        'dump_publication_type',
        attribute='resource_type.subtype',
        validate=validate.OneOf(
            choices=ObjectType.get_subtypes('publication')),
    )
    image_type = fields.Method(
        'dump_image_type',
        attribute='resource_type.subtype',
        validate=validate.OneOf(choices=ObjectType.get_subtypes('image')),
    )

    # Overwrite subjects from common schema.
    subjects = fields.Nested(SubjectSchemaV1, many=True)

    license = fields.Method('dump_license', 'load_license')
    communities = fields.Method('dump_communities', 'load_communities')
    grants = fields.Method('dump_grants', 'load_grants')

    prereserve_doi = fields.Method('dump_prereservedoi', 'load_prereservedoi')

    journal_title = TrimmedString(attribute='journal.title')
    journal_volume = TrimmedString(attribute='journal.volume')
    journal_issue = TrimmedString(attribute='journal.issue')
    journal_pages = TrimmedString(attribute='journal.pages')

    conference_title = TrimmedString(attribute='meeting.title')
    conference_acronym = TrimmedString(attribute='meeting.acronym')
    conference_dates = TrimmedString(attribute='meeting.dates')
    conference_place = TrimmedString(attribute='meeting.place')
    conference_url = fields.Url(attribute='meeting.url')
    conference_session = TrimmedString(attribute='meeting.session')
    conference_session_part = TrimmedString(
        attribute='meeting.session_part')

    imprint_isbn = TrimmedString(attribute='imprint.isbn')
    imprint_place = TrimmedString(attribute='imprint.place')
    imprint_publisher = TrimmedString(attribute='imprint.publisher')

    partof_pages = TrimmedString(attribute='part_of.pages')
    partof_title = TrimmedString(attribute='part_of.title')

    thesis_university = TrimmedString(attribute='thesis.university')
    thesis_supervisors = fields.Nested(
        common.PersonSchemaV1, many=True, attribute='thesis.supervisors')

    def _dump_subtype(self, obj, type_):
        """Get subtype."""
        if obj.get('resource_type', {}).get('type') == type_:
            return obj.get('resource_type', {}).get('subtype', missing)
        return missing

    def dump_publication_type(self, obj):
        """Get publication type."""
        return self._dump_subtype(obj, 'publication')

    def dump_image_type(self, obj):
        """Get publication type."""
        return self._dump_subtype(obj, 'image')

    def dump_license(self, obj):
        """Dump license."""
        return obj.get('license', {}).get('id', missing)

    def load_license(self, data):
        """Load license."""
        if not isinstance(data, six.string_types):
            raise ValidationError(_('Not a string.'))
        return {'$ref': 'https://dx.zenodo.org/licenses/{0}'.format(data)}

    def dump_grants(self, obj):
        """Get grants."""
        res = []
        for g in obj.get('grants', []):
            if g.get('program', {}) == 'FP7' and \
                    g.get('funder', {}).get('doi') == '10.13039/501100000780':
                res.append(dict(id=g['code']))
            else:
                res.append(dict(id=g['internal_id']))
        return res or missing

    def load_grants(self, data):
        """Load grants."""
        if not isinstance(data, list):
            raise ValidationError(_('Not a list.'))
        res = []
        for g in data:
            if not isinstance(g, dict):
                raise ValidationError(_('Element not an object.'))
            g = g.get('id')
            if not g:
                continue
            # FP7 project grant
            if not g.startswith('10.13039/'):
                g = '10.13039/501100000780::{0}'.format(g)
            res.append({'$ref': 'https://dx.zenodo.org/grants/{0}'.format(g)})
        return res or missing

    def dump_communities(self, obj):
        """Dump communities type."""
        return [dict(identifier=x) for x in obj.get('communities', [])] \
            or missing

    def load_communities(self, data):
        """Load communities type."""
        if not isinstance(data, list):
            raise ValidationError(_('Not a list.'))
        return list(sorted([
            x['identifier'] for x in data if x.get('identifier')
        ])) or missing

    def dump_prereservedoi(self, obj):
        """Dump pre-reserved DOI."""
        recid = obj.get('recid')
        if recid:
            prefix = None
            if not current_app:
                prefix = '10.5072'  # Test prefix

            return dict(
                recid=recid,
                doi=doi_generator(recid, prefix=prefix),
            )
        return missing

    def load_prereservedoi(self, obj):
        """Load pre-reserved DOI.

        The value is not important as we do not store it. Since the deposit and
        record id are now the same
        """
        return missing

    @pre_dump()
    def predump_related_identifiers(self, data):
        """Split related/alternate identifiers.

        This ensures that we can just use the base schemas definitions of
        related/alternate identifies.
        """
        relids = data.pop('related_identifiers', [])
        alids = data.pop('alternate_identifiers', [])

        for a in alids:
            a['relation'] = 'isAlternateIdentifier'

        if relids or alids:
            data['related_identifiers'] = relids + alids

        return data

    @pre_load()
    def preload_related_identifiers(self, data):
        """Split related/alternate identifiers.

        This ensures that we can just use the base schemas definitions of
        related/alternate identifies for loading.
        """
        # Legacy API does not accept alternate_identifiers, so force delete it.
        data.pop('alternate_identifiers', None)

        for r in data.pop('related_identifiers', []):
            # Problem that API accepted one relation while documentation
            # presented a different relation.
            if r.get('relation') in [
                    'isAlternativeIdentifier', 'isAlternateIdentifier']:
                k = 'alternate_identifiers'
            else:
                k = 'related_identifiers'

            data.setdefault(k, [])
            data[k].append(r)

    @pre_load()
    def preload_resource_type(self, data):
        """Prepare data for easier deserialization."""
        if data.get('upload_type') == 'publication':
            data.pop('image_type', None)
        elif data.get('upload_type') == 'image':
            data.pop('publication_type', None)

    @post_load()
    def merge_keys(self, data):
        """Merge dot keys."""
        prefixes = [
            'resource_type',
            'journal',
            'meeting',
            'imprint',
            'part_of',
            'thesis',
        ]

        for p in prefixes:
            for k in list(data.keys()):
                if k.startswith('{0}.'.format(p)):
                    key, subkey = k.split('.')
                    if key not in data:
                        data[key] = dict()
                    data[key][subkey] = data.pop(k)

        # Pre-reserve DOI is implemented differently now.
        data.pop('prereserve_doi', None)

    @validates('communities')
    def validate_communities(self, values):
        """Validate communities."""
        for v in values:
            if not isinstance(v, six.string_types):
                raise ValidationError(_('Invalid community identifier.'))

    @validates_schema
    def validate_data(self, obj):
        """Validate resource type."""
        type_ = obj.get('resource_type.type')
        if type_ in ['publication', 'image']:
            type_dict = {
                'type': type_,
                'subtype': obj.get('resource_type.subtype'),
            }
        else:
            type_dict = {'type': type_}

        if ObjectType.get_by_dict(type_dict) is None:
            raise ValidationError(
                _('Invalid upload, publication or image type.'))


class LegacyRecordSchemaV1(common.CommonRecordSchemaV1):
    """Legacy JSON schema (used by deposit)."""

    doi_url = DOILink(attribute='metadata.doi', dump_only=True)
    files = fields.List(
        fields.Nested(FileSchemaV1), default=[], dump_only=True)
    metadata = fields.Nested(LegacyMetadataSchemaV1)
    modified = fields.Str(attribute='updated', dump_only=True)
    owner = fields.Method('dump_owners', dump_only=True)
    record_id = fields.Integer(attribute='metadata.recid', dump_only=True)
    record_url = fields.String(dump_only=True)
    state = fields.Method('dump_state', dump_only=True)
    submitted = fields.Function(
        lambda o: o['metadata'].get(
            '_deposit', {}).get('status', 'draft') == 'published',
        dump_only=True
    )
    title = fields.String(
        attribute='metadata.title', default='', dump_only=True)

    def dump_state(self, o):
        """Get state of deposit."""
        if o['metadata'].get('_deposit', {}).get('status', 'draft') == 'draft':
            if o['metadata'].get('_deposit', {}).get('pid', {}):
                return 'inprogress'
            else:
                return 'unsubmitted'
        return 'done'

    def dump_owners(self, obj):
        """Get owners."""
        if '_deposit' in obj['metadata']:
            try:
                return obj['metadata']['_deposit'].get('owners', [])[0]
            except IndexError:
                return None
        elif 'owners' in obj['metadata']:
            return obj['metadata']['owners'][0]
        return None
