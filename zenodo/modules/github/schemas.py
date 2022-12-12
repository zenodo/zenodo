# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016-2021 CERN.
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

"""GitHub schemas."""

from __future__ import absolute_import, print_function, unicode_literals

import arrow
import six
from invenio_records_rest.schemas.fields import GenMethod
from marshmallow import Schema, ValidationError, fields, missing, post_dump, \
    post_load, pre_dump, pre_load, validate, validates, validates_schema

from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers.fields import DateString, \
    PersistentId, SanitizedHTML, SanitizedUnicode
from zenodo.modules.records.serializers.schemas.common import RefResolverMixin


class AuthorSchema(Schema):
    """Schema for a person."""

    name = GenMethod(deserialize='load_name')
    affiliation = SanitizedUnicode()
    orcid = PersistentId(scheme='ORCID')

    def load_name(self, value, data):
        """Load name field."""
        family_name = data.get('family-names')
        given_name = data.get('given-names')
        org_name = data.get('name')
        if org_name:
            return org_name
        if family_name and given_name:
            return u'{}, {}'.format(family_name, given_name)
        return family_name or given_name

    @validates_schema
    def validate_data(self, data):
        """Validate schema."""
        name = data.get('name')
        if not name:
            raise ValidationError(
                'Name is required.',
                field_names=['name']
            )


class CitationMetadataSchema(Schema, RefResolverMixin):
    """Citation metadata schema."""

    description = SanitizedHTML(load_from='abstract')
    creators = fields.Nested(
        AuthorSchema, many=True, load_from='authors')
    keywords = fields.List(SanitizedUnicode())
    license = SanitizedUnicode()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=3))
    notes = SanitizedHTML(load_from='message')

    # TODO: Add later
    # alternate_identifiers = fields.Raw(load_from='identifiers')
    # related_identifiers = fields.Raw(load_from='references')

    subschema = {
        "audiovisual": "video",
        "art": "other",
        "bill": "other",
        "blog": "other",
        "catalogue": "other",
        "conference-paper": "conference",
        "database": "data",
        "dictionary": "other",
        "edited-work": "other",
        "encyclopedia": "other",
        "film-broadcast": "video",
        "government-document": "other",
        "grant": "other",
        "hearing": "other",
        "historical-work": "other",
        "legal-case": "other",
        "legal-rule": "other",
        "magazine-article": "other",
        "manual": "other",
        "map": "other",
        "multimedia": "video",
        "music": "other",
        "newspaper-article": "other",
        "pamphlet": "other",
        "patent": "other",
        "personal-communication": "other",
        "proceedings": "other",
        "report": "other",
        "serial": "other",
        "slides": "other",
        "software-code": "software",
        "software-container": "software",
        "software-executable": "software",
        "software-virtual-machine": "software",
        "sound-recording": "other",
        "standard": "other",
        "statute": "other",
        "website": "other"
    }

    # @pre_load()
    # def preload_related_identifiers(self, data):
    #     """Default publication date."""
    #     final = []
    #     for reference in data['references']:
    #         resource_type = reference['type']
    #         if self.subschema.get(resource_type):
    #             resource_type = self.subschema[resource_type]
    #         else:
    #             resource_type = ObjectType.get_cff_type(resource_type)
    #         # data-type grab instead?
    #         for item in reference['identifiers']:
    #             schemes = idutils.detect_identifier_schemes(item['value'])
    #             if not schemes or (item['type'] not in schemes):
    #                 errors = self.context['release'].errors
    #                 cff_errors = errors.get('CITATION.cff', [])
    #                 cff_errors.append(
    #                     'We could not process the identifier: {} in our system'
    #                     .format(item['value']))
    #                 errors['CITATION.cff'] = cff_errors
    #                 continue
    #             final.append({
    #                 'identifier': item['value'],
    #                 'scheme': item['type'],
    #                 'resource_type': resource_type,
    #                 'relation': 'references'
    #             })
    #     data['references'] = final

    # @pre_load()
    # def preload_alternate_identifiers(self, data):
    #     """Default publication date."""
    #     final = []
    #     resource_type = data.get('type', 'other')
    #     if self.subschema.get(resource_type):
    #         resource_type = self.subschema[resource_type]
    #     else:
    #         resource_type = ObjectType.get_cff_type(resource_type)
    #     # data-type grab instead?

    #     for item in data.get('identifiers', []):
    #         schemes = idutils.detect_identifier_schemes(item['value'])
    #         if not schemes or (item['type'] not in schemes):
    #             errors = self.context['release'].errors
    #             cff_errors = errors.get('CITATION.cff', [])
    #             cff_errors.append(
    #                 'We could not process the identifier: {} in our system'
    #                 .format(item['value']))
    #             errors['CITATION.cff'] = cff_errors
    #             continue
    #         final.append({
    #             'identifier': item['value'],
    #             'scheme': item['type'],
    #             'resource_type': resource_type
    #             })
    #     data['identifiers'] = final
