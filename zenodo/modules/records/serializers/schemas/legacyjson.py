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

from __future__ import absolute_import, print_function, unicode_literals

import six
from flask import current_app, url_for
from flask_babelex import lazy_gettext as _
from invenio_communities.models import Community
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from marshmallow import Schema, ValidationError, fields, missing, post_dump, \
    post_load, pre_dump, pre_load, validate, validates, validates_schema
from werkzeug.routing import BuildError

from zenodo.modules.records.models import AccessRight, ObjectType
from zenodo.modules.records.utils import is_valid_openaire_type

from ...minters import doi_generator
from ..fields import DOILink, SanitizedUnicode, SanitizedUrl
from . import common


class FileSchemaV1(Schema):
    """Schema for files depositions."""

    id = fields.String(attribute='file_id', dump_only=True)
    filename = SanitizedUnicode(attribute='key', dump_only=True)
    filesize = fields.Integer(attribute='size', dump_only=True)
    checksum = fields.Method('dump_checksum', dump_only=True)
    links = fields.Method('dump_links', dump_only=True)

    def dump_checksum(self, obj):
        """Dump checksum."""
        checksum = obj.get('checksum')
        if not checksum:
            return missing

        algo, hashval = checksum.split(':')
        if algo != 'md5':
            return missing
        return hashval

    def dump_links(self, obj):
        """Dump links."""
        links = {}

        try:
            links['download'] = url_for(
                'invenio_files_rest.object_api',
                bucket_id=obj.get('bucket'),
                key=obj.get('key'),
                _external=True,
            )
            links['self'] = url_for(
                'invenio_deposit_rest.depid_file',
                pid_value=self.context['pid'].pid_value,
                key=obj.get('file_id'),
                _external=True,
            )
        except BuildError:
            pass

        if not links:
            return missing
        return links


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
    openaire_type = fields.Method(
        'dump_openaire_type',
        attribute='resource_type.openaire_subtype'
    )

    license = fields.Method('dump_license', 'load_license')
    communities = fields.Method('dump_communities', 'load_communities')
    grants = fields.Method('dump_grants', 'load_grants')

    prereserve_doi = fields.Method('dump_prereservedoi', 'load_prereservedoi')

    journal_title = SanitizedUnicode(attribute='journal.title')
    journal_volume = SanitizedUnicode(attribute='journal.volume')
    journal_issue = SanitizedUnicode(attribute='journal.issue')
    journal_pages = SanitizedUnicode(attribute='journal.pages')

    conference_title = SanitizedUnicode(attribute='meeting.title')
    conference_acronym = SanitizedUnicode(attribute='meeting.acronym')
    conference_dates = SanitizedUnicode(attribute='meeting.dates')
    conference_place = SanitizedUnicode(attribute='meeting.place')
    conference_url = SanitizedUrl(attribute='meeting.url')
    conference_session = SanitizedUnicode(attribute='meeting.session')
    conference_session_part = SanitizedUnicode(
        attribute='meeting.session_part')

    imprint_isbn = SanitizedUnicode(attribute='imprint.isbn')
    imprint_place = SanitizedUnicode(attribute='imprint.place')
    imprint_publisher = SanitizedUnicode(attribute='imprint.publisher')

    partof_pages = SanitizedUnicode(attribute='part_of.pages')
    partof_title = SanitizedUnicode(attribute='part_of.title')

    thesis_university = SanitizedUnicode(attribute='thesis.university')
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

    def dump_openaire_type(self, obj):
        """Get OpenAIRE type."""
        return obj.get('resource_type', {}).get('openaire_subtype', missing)

    def dump_license(self, obj):
        """Dump license."""
        return obj.get('license', {}).get('id', missing)

    def load_license(self, data):
        """Load license."""
        if isinstance(data, six.string_types):
            license = data
        if isinstance(data, dict):
            license = data['id']
        return {'$ref': 'https://dx.zenodo.org/licenses/{0}'.format(license)}

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
        result = set()
        errors = set()
        for g in data:
            if not isinstance(g, dict):
                raise ValidationError(_('Element not an object.'))
            g = g.get('id')
            if not g:
                continue
            # FP7 project grant
            if not g.startswith('10.13039/'):
                g = '10.13039/501100000780::{0}'.format(g)
            # Check that the PID exists
            grant_pid = PersistentIdentifier.query.filter_by(
                pid_type='grant', pid_value=g).one_or_none()
            if not grant_pid or grant_pid.status != PIDStatus.REGISTERED:
                errors.add(g)
                continue
            result.add(g)
        if errors:
            raise ValidationError(
                'Invalid grant ID(s): {0}'.format(', '.join(errors)),
                field_names='grants')
        return [{'$ref': 'https://dx.zenodo.org/grants/{0}'.format(grant_id)}
                for grant_id in result] or missing

    def dump_communities(self, obj):
        """Dump communities type."""
        return [dict(identifier=x) for x in obj.get('communities', [])] \
            or missing

    def load_communities(self, data):
        """Load communities type."""
        if not isinstance(data, list):
            raise ValidationError(_('Not a list.'))
        invalid_format_comms = [
            c for c in data if not (isinstance(c, dict) and 'identifier' in c)]
        if invalid_format_comms:
            raise ValidationError(
                'Invalid community format: {}.'.format(invalid_format_comms),
                field_names='communities')

        comm_ids = list(sorted([
            x['identifier'] for x in data if x.get('identifier')
        ]))
        errors = {c for c in comm_ids if not Community.get(c)}
        if errors:
            raise ValidationError(
                'Invalid communities: {0}'.format(', '.join(errors)),
                field_names='communities')
        return comm_ids or missing

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
                r.pop('relation')
            else:
                k = 'related_identifiers'

            data.setdefault(k, [])
            data[k].append(r)

    @pre_load()
    def preload_resource_type(self, data):
        """Prepare data for easier deserialization."""
        if data.get('upload_type') != 'publication':
            data.pop('publication_type', None)
        if data.get('upload_type') != 'image':
            data.pop('image_type', None)

    @pre_load()
    def preload_license(self, data):
        """Default license."""
        acc = data.get('access_right', AccessRight.OPEN)
        if acc in [AccessRight.OPEN, AccessRight.EMBARGOED]:
            if 'license' not in data:
                if data.get('upload_type') == 'dataset':
                    data['license'] = 'CC0-1.0'
                else:
                    data['license'] = 'CC-BY-4.0'

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
                raise ValidationError(
                    _('Invalid community identifier.'),
                    field_names=['communities']
                )

    @validates_schema
    def validate_data(self, obj):
        """Validate resource type."""
        type_ = obj.get('resource_type', {}).get('type')
        if type_ in ['publication', 'image']:
            type_dict = {
                'type': type_,
                'subtype': obj.get('resource_type', {}).get('subtype')
            }
            field_names = ['{0}_type'.format(type_)]
        else:
            type_dict = {'type': type_}
            field_names = ['upload_type']

        if ObjectType.get_by_dict(type_dict) is None:
            raise ValidationError(
                _('Invalid upload, publication or image type.'),
                field_names=field_names,
            )
        if not is_valid_openaire_type(obj.get('resource_type', {}),
                                      obj.get('communities', [])):
            raise ValidationError(
                _('Invalid OpenAIRE subtype.'),
                field_names=['openaire_subtype'],
            )


class LegacyRecordSchemaV1(common.CommonRecordSchemaV1):
    """Legacy JSON schema (used by deposit)."""

    doi_url = DOILink(attribute='metadata.doi', dump_only=True)
    files = fields.List(
        fields.Nested(FileSchemaV1), dump_only=True)
    metadata = fields.Nested(LegacyMetadataSchemaV1)
    modified = fields.Str(attribute='updated', dump_only=True)
    owner = fields.Method('dump_owners', dump_only=True)
    record_id = fields.Integer(attribute='metadata.recid', dump_only=True)
    record_url = fields.String(dump_only=True)
    state = fields.Method('dump_state', dump_only=True)
    submitted = fields.Function(
        lambda o: o['metadata'].get(
            '_deposit', {}).get('pid') is not None,
        dump_only=True
    )
    title = SanitizedUnicode(
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


class DepositFormSchemaV1(LegacyRecordSchemaV1):
    """Schema for deposit form JSON."""

    @post_dump()
    def remove_envelope(self, data):
        """Remove envelope."""
        if 'metadata' in data:
            data = data['metadata']
        return data


class GitHubRecordSchemaV1(DepositFormSchemaV1):
    """JSON which can be added to the .zenodo.json file in a repository."""

    @post_dump()
    def remove_envelope(self, data):
        """Remove envelope."""
        data = super(GitHubRecordSchemaV1, self).remove_envelope(data)
        for k in ['doi', 'prereserve_doi']:
            if k in data:
                del data[k]
        return data
