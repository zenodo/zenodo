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

"""Zenodo record JSON schema."""

from __future__ import absolute_import, print_function

from marshmallow import Schema, fields

from .legacy import JournalSchemaV1, PersonSchemaV1, \
    RelatedIdentifierSchemaV1, PartOfSchemaV1


class ZenodoPersonSchemaV1(PersonSchemaV1):
    """Schema for a Zenodo person."""

    familyname = fields.String()
    givennames = fields.String()


class ZenodoContributorSchemaV1(ZenodoPersonSchemaV1):
    """Schema for a contributor."""

    type = fields.String()


class ZenodoMeetingSchemaV1(Schema):
    """Schema for a journal."""

    title = fields.String()
    acronym = fields.String()
    dates = fields.String()
    place = fields.String()
    url = fields.String()
    session = fields.String()
    session_part = fields.String()


class ZenodoJournalSchemaV1(JournalSchemaV1):
    """"Schema for Zenodo journals."""

    year = fields.String()


class ZenodoRelatedIdentifierSchemaV1(RelatedIdentifierSchemaV1):
    """Schema for a related identifier."""

    scheme = fields.String()


class ZenodoSubjectSchemaV1(Schema):
    """Schema for a Zenodo subject."""

    term = fields.String()
    identifier = fields.String()
    scheme = fields.String()


class ZenodoResourceTypeSchemaV1(Schema):
    """Schema for a resource type."""

    type = fields.String()
    subtype = fields.String()


class ZenodoLicenseSchemaV1(Schema):
    """Schema for licenses."""

    identifier = fields.String()
    license = fields.String()
    source = fields.String()
    url = fields.String()


class ZenodoRelatedIdentifierSchemaV1(RelatedIdentifierSchemaV1):
    """Schema for related identifiers."""

    scheme = fields.String()


class ZenodoAlternateIdentifierSchemaV1(Schema):
    """Schema for alternate identifiers."""

    identifier = fields.String()
    scheme = fields.String()


class ZenodoReferenceSchemaV1(Schema):
    """Schema for Zenodo references."""

    raw_reference = fields.String()


class ZenodoPartOfSchemaV1(PartOfSchemaV1):
    """Schema for PartOf."""

    publisher = fields.String()
    isbn = fields.String()
    place = fields.String()
    year = fields.String()


class ZenodoImprintSchemaV1(Schema):
    """Schema for Imprint."""

    publisher = fields.String()
    place = fields.String()


class ZenodoDepositionFileSchemaV1(Schema):
    """Schema for Zenodo deposition files."""

    bucket = fields.String()
    filename = fields.String()
    version_id = fields.String()
    size = fields.Integer()
    checksum = fields.String()
    previewer = fields.String()
    type = fields.String()


class ZenodoRecordSchemaV1(Schema):
    """Schema for Zenodo records."""

    recid = fields.String()
    doi = fields.String()
    isbn = fields.String()
    altmetric_id = fields.String()
    resource_type = fields.Nested(ZenodoResourceTypeSchemaV1)
    type = fields.String()
    publication_date = fields.String()

    publication_type = fields.String()

    title = fields.String()
    creators = fields.List(fields.Nested(ZenodoPersonSchemaV1))
    description = fields.String()
    keywords = fields.List(fields.String)
    subjects = fields.List(fields.Nested(ZenodoSubjectSchemaV1))
    notes = fields.String()
    language = fields.String()

    access_right = fields.String()

    embargo_date = fields.String()

    access_conditions = fields.String()
    license = fields.Nested(ZenodoLicenseSchemaV1)
    communities = fields.List(fields.String)
    provisional_communities = fields.List(fields.String)
    grants = fields.List(fields.String)
    related_identifiers = fields.List(
            fields.Nested(ZenodoRelatedIdentifierSchemaV1))
    alternate_identifiers = fields.List(
            fields.Nested(ZenodoAlternateIdentifierSchemaV1))
    contributors = fields.List(fields.Nested(ZenodoPersonSchemaV1))
    references = fields.List(fields.Nested(ZenodoReferenceSchemaV1))
    journal = fields.Nested(ZenodoJournalSchemaV1)
    meetings = fields.Nested(ZenodoMeetingSchemaV1)
    part_of = fields.Nested(ZenodoPartOfSchemaV1)
    imprint = fields.Nested(ZenodoImprintSchemaV1)
    thesis_university = fields.String()
    thesis_supervisors = fields.List(fields.Nested(ZenodoPersonSchemaV1))
    files = fields.List(fields.Nested(ZenodoDepositionFileSchemaV1))
    owners = fields.List(fields.Integer)
