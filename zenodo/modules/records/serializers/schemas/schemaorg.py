# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo schema.org marshmallow schema."""

from __future__ import absolute_import, print_function, unicode_literals

import idutils
import pycountry
from flask import current_app
from marshmallow import Schema, fields, missing

from ...models import ObjectType
from ..fields import DateString, SanitizedHTML, SanitizedUnicode
from .common import format_pid_link


def _serialize_identifiers(ids, relations=None):
    """Serialize identifiers to URLs."""
    relations = relations or []
    return [{'@type': 'CreativeWork',
             '@id': idutils.to_url(i['identifier'], i['scheme'])}
            for i in ids if i['relation'] in relations and 'scheme' in i]


class Person(Schema):
    """Person schema."""

    id = fields.Method('get_id')
    type_ = fields.Constant('Person', dump_to="@type")
    name = SanitizedUnicode()
    affiliation = SanitizedUnicode()

    def get_id(self, obj):
        """Get URL for the person's ORCID or GND."""
        orcid = obj.get('orcid')
        gnd = obj.get('gnd')
        if orcid:
            return idutils.to_url(orcid, 'orcid', 'https')
        if gnd:
            return idutils.to_url(orcid, 'gnd')
        return missing


class Language(Schema):
    """Language schema."""

    type_ = fields.Constant('Language', dump_to="@type")
    name = fields.Method('get_name')
    alternateName = fields.Method('get_alternate_name')

    def get_name(self, obj):
        return pycountry.languages.get(alpha_3=obj).name

    def get_alternate_name(self, obj):
        return obj


class CreativeWork(Schema):
    """Schema for schema.org/CreativeWork type."""

    CONTEXT = "https://schema.org/"

    doi = fields.Method('get_doi', dump_to='@id')

    # NOTE: use `__class__`?
    type_ = fields.Method('get_type', dump_to='@type')
    url = fields.Method('get_url')

    name = SanitizedUnicode(attribute='metadata.title')
    description = SanitizedHTML(attribute='metadata.description')
    context = fields.Method('get_context', dump_to='@context')
    keywords = fields.List(SanitizedUnicode(), attribute='metadata.keywords')

    # TODO: What date?
    # dateCreated
    # dateModified
    datePublished = DateString(attribute='metadata.publication_date')

    # NOTE: could also be  "author"
    creator = fields.Nested(Person, many=True, attribute='metadata.creators')

    version = SanitizedUnicode(attribute='metadata.version')

    inLanguage = fields.Nested(Language, attribute='metadata.language')

    license = SanitizedUnicode(attribute='metadata.license.url')

    citation = fields.Method('get_citation')
    isPartOf = fields.Method('get_is_part_of')
    hasPart = fields.Method('get_has_part')
    sameAs = fields.Method('get_sameAs')

    # NOTE: reverse of subjectOf
    about = fields.Method('get_subjects')

    contributor = fields.Nested(
        Person, many=True, attribute='metadata.contributors')

    # NOTE: editor from "contributors"?
    # editor

    # NOTE: Zenodo or similar?
    # provider
    # publisher

    # NOTE: "grants" or aggregation of "funders"? Could go in "sponsor" as well
    # Relevant codemeta issue: https://github.com/codemeta/codemeta/issues/160
    # funder

    # NOTE: Zenodo communities?
    # sourceOrganization

    def get_context(self, obj):
        """Returns the value for '@context' value."""
        return self.CONTEXT

    def get_doi(self, obj):
        """Get DOI of the record."""
        data = obj['metadata']
        return idutils.to_url(data['doi'], 'doi') if data['doi'] else missing

    def get_type(self, obj):
        """Get schema.org type of the record."""
        data = obj['metadata']
        obj_type = ObjectType.get_by_dict(data['resource_type'])
        return (obj_type['schema.org'][len(self.CONTEXT):]
                if obj_type else missing)

    def get_url(self, obj):
        """Get Zenodo URL of the record."""
        recid = obj.get('recid')
        return format_pid_link(
            current_app.config['RECORDS_UI_ENDPOINT'], recid
        ) if recid else missing

    def get_citation(self, obj):
        """Get citations of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        return _serialize_identifiers(relids, {'cites', 'references'})

    def get_is_part_of(self, obj):
        """Get records that this record is part of."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        return _serialize_identifiers(relids, {'isPartOf'})

    def get_has_part(self, obj):
        """Get parts of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        return _serialize_identifiers(relids, {'hasPart'})

    def get_sameAs(self, obj):
        """Get identical identifiers of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        return [i['@id']
                for i in _serialize_identifiers(relids, {'isIdenticalTo'})]

    def get_subjects(self, obj):
        """Get subjects of the record."""
        subjects = obj.get('metadata', {}).get('related_identifiers', [])
        return _serialize_identifiers(subjects)


class Dataset(CreativeWork):
    pass


class ScholarlyArticle(CreativeWork):

    # NOTE: Same as title?
    headline = SanitizedUnicode(attribute='metadata.title')
    # NOTE: required by Google... could be thumbnail of PDF...
    image = fields.Constant(
        'https://zenodo.org/static/img/logos/zenodo-gradient-round.svg')


class ImageObject(CreativeWork):
    pass


class Book(CreativeWork):
    pass


class PresentationDigitalDocument(CreativeWork):
    pass


class MediaObject(CreativeWork):
    pass


class SoftwareSourceCode(CreativeWork):
    pass


class Photograph(CreativeWork):
    pass
