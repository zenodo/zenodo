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

"""Marshmallow schemas for Legacy JSON to Zenodo record."""

from __future__ import absolute_import, print_function

from datetime import datetime

import idutils
from marshmallow import Schema, fields, missing, post_dump

from zenodo.modules.deposit.loaders.schemas.utils import filter_empty_list, \
    filter_thesis, none_if_empty
from zenodo.modules.records.serializers import fields as zfields


class PersonSchema(Schema):
    """Schema for a person."""

    name = fields.String()
    affiliation = fields.String()
    gnd = fields.String()
    orcid = fields.String()


class ContributorSchema(PersonSchema):
    """Schema for contributors."""

    type = fields.String()


class MeetingSchema(Schema):
    """Schema for a journal."""

    title = fields.String(attribute='conference_title')
    acronym = fields.String(attribute='conference_acronym')
    dates = fields.String(attribute='conference_dates')
    place = fields.String(attribute='conference_place')
    url = fields.String(attribute='conference_url')
    session = fields.String(attribute='conference_session')
    session_part = fields.String(attribute='conference_session_part')


class JournalSchema(Schema):
    """Schema for a journal."""

    title = fields.String(attribute='journal_title')
    volume = fields.String(attribute='journal_volume')
    issue = fields.String(attribute='journal_issue')
    pages = fields.String(attribute='journal_pages')


class AlternateIdentifierSchema(Schema):
    """Schema for alternate identifiers."""

    identifier = fields.String()
    scheme = fields.Method('get_scheme')

    def get_scheme(self, obj):
        """Get scheme."""
        scheme = obj.get('scheme')
        if not scheme and obj.get('identifier'):
            scheme = idutils.detect_identifier_schemes(obj['identifier'])
            if scheme:
                scheme = scheme[0]
        return scheme if scheme else ""


class RelatedIdentifierSchema(AlternateIdentifierSchema):
    """Schema for a related identifier."""

    relation = fields.String()


class SubjectSchema(Schema):
    """Schema for a subject."""

    term = fields.String()
    identifier = fields.String(attribute='id')
    scheme = fields.String()


class LicenseSchema(Schema):
    """Schema for licenses."""

    identifier = fields.String()
    license = fields.String()
    source = fields.String()
    url = fields.String()


class ReferenceSchema(Schema):
    """Schema for references."""

    raw_reference = fields.Function(lambda x: x)


class PartOfSchema(Schema):
    """Schema for PartOf."""

    pages = fields.String(attribute='partof_pages')
    title = fields.String(attribute='partof_title')


class ImprintSchema(Schema):
    """Schema for Imprint."""

    isbn = fields.String(attribute='imprint_isbn')
    place = fields.String(attribute='imprint_place')
    publisher = fields.String(attribute='imprint_publisher')


class ThesisSchema(Schema):
    """Schema for thesis."""

    university = fields.String(attribute='thesis_university')
    supervisors = fields.Nested(
        PersonSchema, attribute='thesis_supervisors', many=True)


class ActionSchema(Schema):
    """Schema for PartOf."""

    prereserve_doi = fields.Method('get_prereserve_doi')

    @staticmethod
    def get_prereserve_doi(obj):
        """Get pre-reserve DOI."""
        # TODO: Review after the Pre-Reserve DOI has been implemented
        return obj.get('prereserve_doi') is not None


class ResourceTypeSchema(Schema):
    """Schema for resource type."""

    type = fields.String(attribute='upload_type')
    subtype = fields.Method('get_subtype')

    def get_subtype(self, obj):
        """Get resource type."""
        type_ = obj.get('upload_type')
        if type_ == 'publication':
            return obj.get('publication_type')
        elif type_ == 'image':
            return obj.get('image_type')
        else:
            return missing


class LegacyRecordSchemaV1(Schema):
    """Marshmallow schema for legacy JSON to Zenodo record."""

    doi = zfields.DOI(attribute='metadata.doi')
    resource_type = fields.Nested(ResourceTypeSchema, attribute='metadata')
    publication_date = fields.String(
        attribute='metadata.publication_date',
        default=datetime.utcnow().date().isoformat())
    title = fields.String(attribute='metadata.title')
    creators = fields.List(
        fields.Nested(PersonSchema),
        attribute='metadata.creators')
    description = fields.String(attribute='metadata.description')
    keywords = fields.List(fields.String, attribute='metadata.keywords')
    subjects = fields.List(
        fields.Nested(SubjectSchema),
        attribute='metadata.subjects')
    notes = fields.String(attribute='metadata.notes')
    access_right = fields.String(attribute='metadata.access_right',
                                 default='open')
    embargo_date = fields.String(attribute='metadata.embargo_date')
    access_conditions = fields.String(attribute='metadata.access_conditions')
    license = fields.Method('get_license')
    communities = fields.List(
        fields.String(attribute='identifier'),
        attribute='metadata.communities'
    )
    grants = fields.Method('get_grants')
    related_identifiers = fields.Method('get_related_identifiers')
    alternate_identifiers = fields.Method('get_alternate_identifiers')
    contributors = fields.List(
        fields.Nested(ContributorSchema),
        attribute='metadata.contributors')
    references = fields.List(
        fields.Nested(ReferenceSchema),
        attribute='metadata.references')
    journal = fields.Nested(JournalSchema, attribute='metadata')
    meeting = fields.Nested(MeetingSchema, attribute='metadata')
    part_of = fields.Nested(PartOfSchema, attribute='metadata')
    imprint = fields.Nested(ImprintSchema, attribute='metadata')
    thesis = fields.Nested(ThesisSchema, attribute='metadata')
    # _deposit_actions = fields.Nested(ActionSchema, attribute='metadata')

    def get_grants(self, obj):
        """Get grant."""
        grants = obj.get('metadata', {}).get('grants', [])

        res = []
        for g in grants:
            if g.get('id'):
                grant_id = g['id']
                # Legacy support (any id without FundRef DOI is an FP7 grant
                # id).
                if not grant_id.startswith('10.13039/'):
                    grant_id = '10.13039/501100000780::{0}'.format(grant_id)

                res.append({
                    '$ref': 'https://dx.zenodo.org/grants/{0}'.format(grant_id)
                })
        return res if res else missing

    def get_license(self, obj):
        """Get license."""
        l_id = obj.get('metadata', {}).get('license')
        if l_id:
            return {
                '$ref': 'https://dx.zenodo.org/licenses/{0}'.format(l_id)
            }
        return missing

    def split_related_identifers(self, obj, schema_class, test):
        """Split into related/alternate identifiers."""
        res = []
        for r in obj.get('metadata', {}).get('related_identifiers', []):
            # Problem that API accepted one relation while documentation
            # presented a different relation.
            if test(r.get('relation'), [
                    'isAlternativeIdentifier', 'isAlternateIdentifier']):
                res.append(schema_class().dump(r).data)
        return res if res else missing

    def get_related_identifiers(self, obj):
        """Get related identifiers."""
        return self.split_related_identifers(
            obj, RelatedIdentifierSchema, lambda a, b: a not in b)

    def get_alternate_identifiers(self, obj):
        """Get alternate identifiers."""
        return self.split_related_identifers(
            obj, AlternateIdentifierSchema, lambda a, b: a in b)

    def clean_imprint_partof(self, data):
        """Clean imprint and partof."""
        imprint = data.get('imprint', {})
        if data.get('publication_date') and imprint.get('publisher') and \
                imprint.get('place'):
            data['imprint']['year'] = data['publication_date'][:4]

        partof = data.get('part_of', {})
        if partof.get('title'):
            if 'imprint' in data:
                partof.update(data['imprint'])
                del data['imprint']

        return data

    @post_dump(pass_many=False)
    def clean(self, data):
        """Clean empty values."""
        # data = self.clean_imprint_partof(data)

        empty_keys = {
            '_deposit_actions': None,
            'access_conditions': None,
            'alternate_identifiers': filter_empty_list(keys=['identifier', ],
                                                       remove_empty_keys=True),
            'resource_type': None,
            'communities': None,
            'contributors': filter_empty_list(keys=['name', 'affiliation', ]),
            'creators': filter_empty_list(keys=['name', 'affiliation', ]),
            'description': None,
            'grants': None,
            'imprint': none_if_empty(),
            'journal': none_if_empty(keys=['title']),
            'keywords': filter_empty_list(),
            'license': None,
            'meeting': none_if_empty(),
            'notes': None,
            'part_of': none_if_empty(),
            'provisional_communities': None,
            'references': None,
            'related_identifiers': filter_empty_list(keys=['identifier', ],
                                                     remove_empty_keys=True),
            'subjects': filter_empty_list(keys=['term', ]),
            'thesis': filter_thesis(),
        }

        for k, fun in empty_keys.items():
            if k in data:
                if fun is not None:  # Apply the function if provided
                    data[k] = fun(data[k])
                if not data[k]:  # Remove empty items
                    del data[k]

        data['$schema'] = \
            'https://zenodo.org/schemas/deposits/records/record-v1.0.0.json'

        return data
