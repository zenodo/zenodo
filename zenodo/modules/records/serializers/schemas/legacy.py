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

from marshmallow import fields, Schema


def generate_embedded_fields(prefix, schema, attributes={}):
    """Generate the embedded fields for marshmallow."""
    result = {}
    for key, value in schema._declared_fields.iteritems():
        formatted_key = '{0}_{1}'.format(prefix, key)
        if key in attributes:
            value.attribute = attributes[key]
        result[formatted_key] = value
    return result


class PersonSchemaV1(Schema):
    """Schema for a person."""

    name = fields.String()
    affiliation = fields.String()
    gnd = fields.String()
    orcid = fields.String()


class ContributorSchemaV1(PersonSchemaV1):
    """Schema for contributors."""

    type = fields.String()


class ConferenceSchemaV1(Schema):
    """Schema for a journal."""

    title = fields.String()
    acronym = fields.String()
    dates = fields.String()
    place = fields.String()
    url = fields.String()
    session = fields.String()
    session_part = fields.String()


class GrantSchemaV1(Schema):
    """Schema for a grant."""

    id = fields.String()


class ImprintSchemaV1(Schema):
    """Schema for an imprint."""

    publisher = fields.String()
    isbn = fields.String()
    place = fields.String()


class JournalSchemaV1(Schema):
    """Schema for a journal."""

    title = fields.String()
    volume = fields.String()
    issue = fields.String()
    pages = fields.String()


class PartOfSchemaV1(Schema):
    """Schema for PartOf."""

    title = fields.String()
    pages = fields.String()


class RelatedIdentifierSchemaV1(Schema):
    """Schema for a related identifier."""

    relation = fields.String()
    identifier = fields.String()


class ThesisSchemaV1(Schema):
    """Schema for thesis."""

    supervisors = fields.List(fields.Nested(PersonSchemaV1))
    university = fields.String()


class SubjectSchemaV1(Schema):
    """Schema for a subject."""

    term = fields.String()
    identifier = fields.String()
    scheme = fields.String()


class CommunitySchemaV1(Schema):
    """Schema for communities."""

    identifier = fields.String()


class RecordSchemaV1(Schema):
    """Schema for records."""

    id = fields.Integer()
    url = fields.String()


class LegacyDepositionFileSchemaV1(Schema):
    """Schema for files depositions."""

    id = fields.String()
    filename = fields.String(required=True)
    filesize = fields.Integer()
    checksum = fields.String()


LegacyDepositionMetadataSchemaV1 = type(
        'ZenodoDepositionMetadataSchemaV1', (Schema,),
        reduce(lambda d0, d1: dict(d0, **d1),
               (
                   {
                       'upload_type': fields.String(required=True),
                       'publication_type': fields.String(),
                       'image_type': fields.String(),
                       'publication_date': fields.String(required=True),
                       'title': fields.String(required=True),
                       'creators': fields.List(fields.Nested(PersonSchemaV1),
                                               required=True),
                       'description': fields.String(required=True),
                       'access_right': fields.String(required=True),
                       'license': fields.String(),
                       'embargo_date': fields.String(),
                       'access_conditions': fields.String(),
                       'doi': fields.String(),
                       'prereserve_doi': fields.Bool(),
                       'keywords': fields.List(fields.String),
                       'notes': fields.String(),
                       'related_identifiers': fields.List(fields.Nested(
                               RelatedIdentifierSchemaV1)),
                       'contributors': fields.List(fields.Nested(
                               ContributorSchemaV1)),
                       'references': fields.List(fields.String),
                       'communities': fields.List(fields.Nested(
                               CommunitySchemaV1)),
                       'grants': fields.List(fields.Nested(GrantSchemaV1)),
                       'subjects': fields.List(fields.Nested(SubjectSchemaV1)),
                   },
                   generate_embedded_fields('journal', JournalSchemaV1),
                   generate_embedded_fields('conference', ConferenceSchemaV1),
                   generate_embedded_fields('imprint', ImprintSchemaV1),
                   generate_embedded_fields('partof', PartOfSchemaV1),
                   generate_embedded_fields('thesis', ThesisSchemaV1),
               )
               )
)

LegacyDepositionSchemaV1 = type(
        'ZenodoDepositionSchemaV1', (Schema,),
        reduce(lambda d0, d1: dict(d0, **d1),
               (
                   {
                       'created': fields.String(),
                       'doi': fields.String(),
                       'doi_url': fields.String(),
                       'files': fields.List(fields.Nested(
                               LegacyDepositionFileSchemaV1), required=True),
                       'id': fields.Integer(),
                       'metadata': fields.Nested(
                               LegacyDepositionMetadataSchemaV1, required=True),
                       'modified': fields.String(),
                       'owner': fields.Integer(),
                       'state': fields.String(),
                       'submitted': fields.Bool(),
                       'title': fields.String(),
                   },
                   generate_embedded_fields('record', RecordSchemaV1),
               )
               )
)
