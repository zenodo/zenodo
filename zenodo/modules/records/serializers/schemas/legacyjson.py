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

import idutils
from marshmallow import Schema, fields, post_dump


def clean_empty(data, keys):
    """Clean empty values."""
    for k in keys:
            if k in data and not data[k]:
                del data[k]
    return data


class DOILink(fields.Field):
    """DOI link field."""

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return idutils.to_url(value, 'doi')


class PersonSchemaV1(Schema):
    """Schema for a person."""

    name = fields.String()
    affiliation = fields.String()
    gnd = fields.String()
    orcid = fields.String()

    @post_dump(pass_many=False)
    def clean(self, data):
        """Clean empty values."""
        return clean_empty(data, ['orcid', 'gnd', 'affiliation'])


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for contributors."""

    type = fields.String()


class BaseIdentifierSchemeV1(Schema):
    """Base for identifiers."""

    identifier = fields.String()
    scheme = fields.String()


class RelatedIdentifierSchemaV1(BaseIdentifierSchemeV1):
    """Schema for a related identifier."""

    relation = fields.String()


class SubjectSchemaV1(BaseIdentifierSchemeV1):
    """Schema for a subject."""

    term = fields.String()


class FileSchemaV1(Schema):
    """Schema for files depositions."""

    id = fields.String()
    filename = fields.String(attribute='key')
    filesize = fields.Integer(attribute='size')
    checksum = fields.String()


class MetadataSchemaV1(Schema):
    """Legacy JSON metadata."""

    upload_type = fields.String(attribute='resource_type.type')
    publication_type = fields.Method('get_publication_type')
    image_type = fields.Method('get_image_type')
    publication_date = fields.String()
    title = fields.String()
    creators = fields.List(fields.Nested(PersonSchemaV1))
    description = fields.String()
    access_right = fields.String()
    license = fields.String(attribute='license.id')
    embargo_date = fields.String()
    access_conditions = fields.String()
    doi = fields.String()
    prereserve_doi = fields.Bool(attribute='_deposit_actions.prereserve_doi')
    keywords = fields.List(fields.String)
    notes = fields.String()
    related_identifiers = fields.Method('get_related_identifiers')
    contributors = fields.List(fields.Nested(ContributorSchemaV1))
    references = fields.List(fields.String(attribute='raw_reference'))
    communities = fields.Function(
        lambda o: [dict(identifier=x) for x in o.get('communities', [])])
    grants = fields.Method('get_grants')

    journal_title = fields.String(attribute='journal.title')
    journal_volume = fields.String(attribute='journal.volume')
    journal_issue = fields.String(attribute='journal.issue')
    journal_pages = fields.String(attribute='journal.pages')

    conference_title = fields.String(attribute='meetings.title')
    conference_acronym = fields.String(attribute='meetings.acronym')
    conference_dates = fields.String(attribute='meetings.dates')
    conference_place = fields.String(attribute='meetings.place')
    conference_url = fields.String(attribute='meetings.url')
    conference_session = fields.String(attribute='meetings.session')
    conference_session_part = fields.String(
        attribute='meetings.session_part')

    imprint_isbn = fields.String(attribute='imprint.isbn')
    imprint_place = fields.String(attribute='imprint.place')
    imprint_publisher = fields.String(attribute='imprint.publisher')

    partof_isbn = fields.String(attribute='part_of.isbn')
    partof_pages = fields.String(attribute='part_of.pages')
    partof_place = fields.String(attribute='part_of.place')
    partof_publisher = fields.String(attribute='part_of.publisher')
    partof_title = fields.String(attribute='part_of.title')

    thesis_university = fields.String()
    thesis_supervisors = fields.List(fields.Nested(PersonSchemaV1))

    subjects = fields.List(fields.Nested(SubjectSchemaV1))

    def get_subtype(self, obj, type_):
        """Get subtype."""
        if obj.get('resource_type', {}).get('type') == type_:
            return obj.get('resource_type', {}).get('subtype')

    def get_publication_type(self, obj):
        """Get publication type."""
        return self.get_subtype(obj, 'publication')

    def get_image_type(self, obj):
        """Get publication type."""
        return self.get_subtype(obj, 'image')

    def get_related_identifiers(self, obj):
        """Get related identifiers."""
        s = RelatedIdentifierSchemaV1()
        res = []
        for i in obj.get('related_identifiers', []):
            res.append(s.dump(i).data)
        for i in obj.get('alternate_identifiers', []):
            v = {'relation': 'isAlternativeIdentifier'}
            v.update(i)
            res.append(s.dump(v).data)
        return res

    def get_grants(self, obj):
        """Get grants."""
        res = []
        for g in obj.get('grants', []):
            if g.get('program', {}) == 'FP7' and \
                    g.get('funder', {}).get('doi') == '10.13039/501100000780':
                res.append(dict(id=g['code']))
            else:
                res.append(dict(id=g['internal_id']))
        return res

    def clean_imprint_partof(self, data):
        """Clean imprint and partof."""
        keys = ['isbn', 'place', 'publisher']

        if data.get('partof_title', '').strip():
            for k in keys:
                pk = 'partof_{0}'.format(k)
                ik = 'imprint_{0}'.format(k)
                if pk in data:
                    data[ik] = data[pk]
                elif ik in data:
                    del data[ik]

        # Make sure keys are removed even if partof_title is empty
        for k in keys:
            pk = 'partof_{0}'.format(k)
            if pk in data:
                del data[pk]

        return data

    @post_dump(pass_many=False)
    def clean(self, data):
        """Clean empty values."""
        data = self.clean_imprint_partof(data)
        empty_keys = [
            'communities',
            'grants',
            'image_type',
            'publication_type',
            'related_identifiers',

        ]
        return clean_empty(data, empty_keys)


def legacy_state(o):
    """Dinamically build legacy state."""
    if o['metadata'].get('_deposit', {}).get('status', 'draft') == 'draft':
        if o['metadata'].get('_deposit', {}).get('pid', {}):
            return 'inprogress'
        else:
            return 'unsubmitted'
    return 'done'

class LegacyJSONSchemaV1(Schema):
    """Legacy JSON schema (used by deposit)."""

    created = fields.Str()
    doi = fields.Str(attribute='metadata.doi')
    doi_url = DOILink(attribute='metadata.doi')
    files = fields.List(fields.Nested(FileSchemaV1))
    # Make into integer
    id = fields.String(attribute='pid.pid_value')
    metadata = fields.Nested(MetadataSchemaV1, attribute='metadata')
    modified = fields.Str(attribute='updated')
    owner = fields.Method('get_owners')
    record_id = fields.Integer(attribute='metadata.recid')
    record_url = fields.String()
    state = fields.Function(legacy_state)
    submitted = fields.Function(
        lambda o: o['metadata'].get(
            '_deposit', {}).get('status', 'draft') == 'published'
    )
    title = fields.String(attribute='metadata.title')
    links = fields.Raw()

    def get_owners(self, obj):
        """Get owners."""
        if '_deposit' in obj['metadata']:
            try:
                return obj['metadata']['_deposit'].get('owners', [])[0]
            except IndexError:
                return None
        elif 'owners' in obj['metadata']:
            return obj['metadata']['owners'][0]
        return None
