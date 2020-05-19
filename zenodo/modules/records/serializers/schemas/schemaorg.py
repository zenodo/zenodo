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
from flask import current_app, request
from marshmallow import Schema, fields, missing, pre_dump

from ...models import ObjectType
from ..fields import DateString, SanitizedHTML, SanitizedUnicode
from .common import ui_link_for


def _serialize_identifiers(ids, relations=None):
    """Serialize related and alternate identifiers to URLs.

    :param ids: List of related_identifier or alternate_identifier objects.
    :param relations: if not None, will only select IDs of specific relation
    :returns: List of identifiers in schema.org format.
    :rtype dict:
    """
    relations = relations or []
    ids = [{'@type': 'CreativeWork',
             '@id': idutils.to_url(i['identifier'], i['scheme'], 'https')}
            for i in ids if (not relations or i['relation'] in relations) and 'scheme' in i]
    return [id_ for id_ in ids if id_['@id']]


def _serialize_subjects(ids):
    """Serialize subjects to URLs."""
    return [{'@type': 'CreativeWork',
             '@id': idutils.to_url(i['identifier'], i['scheme'], 'https')}
            for i in ids if 'scheme' in i]


def format_files_rest_link(bucket, key, scheme='https'):
    """Format Files REST URL."""
    return current_app.config['FILES_REST_ENDPOINT'].format(
        scheme=scheme, host=request.host, bucket=bucket, key=key)


class Person(Schema):
    """Person schema (schema.org/Person)."""

    id_ = fields.Method('get_id', dump_to='@id')
    type_ = fields.Constant('Person', dump_to='@type')
    name = SanitizedUnicode()
    affiliation = SanitizedUnicode()

    def get_id(self, obj):
        """Get URL for the person's ORCID or GND."""
        orcid = obj.get('orcid')
        gnd = obj.get('gnd')
        if orcid:
            return idutils.to_url(orcid, 'orcid', 'https')
        if gnd:
            return idutils.to_url(gnd, 'gnd', 'https')
        return missing


class Language(Schema):
    """Language schema (schema.org/Language)."""

    type_ = fields.Constant('Language', dump_to="@type")
    name = fields.Method('get_name')
    alternateName = fields.Method('get_alternate_name')

    def get_name(self, obj):
        """Get the language human-readable name."""
        lang = pycountry.languages.get(alpha_3=obj)
        if lang:
            return lang.name

    def get_alternate_name(self, obj):
        """Get the lanugage code."""
        return obj


class Place(Schema):
    """Marshmallow schema for schema.org/Place."""

    type_ = fields.Constant('Place', dump_to='@type')
    geo = fields.Method('get_geo')
    name = SanitizedUnicode(attribute='place')

    def get_geo(self, obj):
        """Generate geo field."""
        if obj.get('lat') and obj.get('lon'):
            return {
                '@type': 'GeoCoordinates',
                'latitude': obj['lat'],
                'longitude': obj['lon']
            }
        else:
            return missing


class CreativeWork(Schema):
    """Schema for schema.org/CreativeWork type."""

    CONTEXT = "https://schema.org/"

    identifier = fields.Method('get_doi', dump_to='identifier')
    id_ = fields.Method('get_doi', dump_to='@id')

    # NOTE: use `__class__`?
    type_ = fields.Method('get_type', dump_to='@type')
    url = fields.Method('get_url')

    name = SanitizedUnicode(attribute='metadata.title')
    description = SanitizedHTML(attribute='metadata.description')
    context = fields.Method('get_context', dump_to='@context')
    keywords = fields.List(SanitizedUnicode(), attribute='metadata.keywords')
    spatial = fields.Nested(Place, many=True, attribute='metadata.locations')

    # TODO: What date?
    # dateCreated
    # dateModified
    datePublished = DateString(attribute='metadata.publication_date')

    temporal = fields.Method('get_dates')

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

    def get_dates(self, obj):
        """Get dates of the record."""
        dates = []
        for interval in obj['metadata'].get('dates', []):
            start = interval.get('start') or '..'
            end = interval.get('end') or '..'
            if start != '..' and end != '..' and start == end:
                dates.append(start)
            else:
                dates.append(start + '/' + end)
        return dates or missing

    def get_context(self, obj):
        """Returns the value for '@context' value."""
        return self.CONTEXT

    def get_doi(self, obj):
        """Get DOI of the record."""
        data = obj['metadata']
        return idutils.to_url(data['doi'], 'doi', 'https') \
            if data.get('doi') \
            else missing

    def get_type(self, obj):
        """Get schema.org type of the record."""
        data = obj['metadata']
        obj_type = ObjectType.get_by_dict(data['resource_type'])
        return (obj_type['schema.org'][len(self.CONTEXT):]
                if obj_type else missing)

    def get_url(self, obj):
        """Get Zenodo URL of the record."""
        recid = obj.get('metadata', {}).get('recid')
        return ui_link_for('record_html', id=recid) if recid else missing

    def get_citation(self, obj):
        """Get citations of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        ids = _serialize_identifiers(relids, {'cites', 'references'})
        return ids or missing

    def get_is_part_of(self, obj):
        """Get records that this record is part of."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        ids = _serialize_identifiers(relids, {'isPartOf'})
        return ids or missing

    def get_has_part(self, obj):
        """Get parts of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        ids = _serialize_identifiers(relids, {'hasPart'})
        return ids or missing

    def get_sameAs(self, obj):
        """Get identical identifiers of the record."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])
        ids = [i['@id']
                for i in _serialize_identifiers(relids, {'isIdenticalTo'})]
        relids = obj.get('metadata', {}).get('alternate_identifiers', [])
        ids += [i['@id'] for i in _serialize_identifiers(relids)]
        return ids or missing

    def get_subjects(self, obj):
        """Get subjects of the record."""
        subjects = obj.get('metadata', {}).get('subjects', [])
        return _serialize_subjects(subjects) or missing


class Distribution(Schema):
    """Marshmallow schema for schema.org/Distribution."""

    type_ = fields.Constant('DataDownload', dump_to='@type')
    encodingFormat = SanitizedUnicode(attribute='type')
    contentUrl = fields.Method('get_content_url')

    def get_content_url(self, obj):
        """Get URL of the file."""
        return format_files_rest_link(bucket=obj['bucket'], key=obj['key'])


class Dataset(CreativeWork):
    """Marshmallow schema for schema.org/Dataset."""

    distribution = fields.Nested(
        Distribution, many=True, attribute='metadata._files')

    measurementTechnique = SanitizedUnicode(attribute='metadata.method')

    @pre_dump
    def hide_closed_files(self, obj):
        """Hide the _files if the record is not Open Access."""
        m = obj['metadata']
        if m['access_right'] != 'open' and '_files' in m:
            del obj['metadata']['_files']


class ScholarlyArticle(CreativeWork):
    """Marshmallow schema for schema.org/ScholarlyArticle."""

    # TODO: Investigate if this should be the same as title
    headline = SanitizedUnicode(attribute='metadata.title')
    image = fields.Constant(
        'https://zenodo.org/static/img/logos/zenodo-gradient-round.svg')


class ImageObject(CreativeWork):
    """Marshmallow schema for schema.org/ImageObject."""

    pass


class Collection(CreativeWork):
    """Marshmallow schema for schema.org/Collection."""

    pass


class Book(CreativeWork):
    """Marshmallow schema for schema.org/Book."""

    pass


class PresentationDigitalDocument(CreativeWork):
    """Marshmallow schema for schema.org/PresentationDigitalDocument."""

    pass


class MediaObject(CreativeWork):
    """Marshmallow schema for schema.org/MediaObject."""

    pass


class SoftwareSourceCode(CreativeWork):
    """Marshmallow schema for schema.org/SoftwareSourceCode."""

    # TODO: Include GitHub url if it's there...
    # related_identifiers.
    codeRepository = fields.Method('get_code_repository_url')

    def get_code_repository_url(self, obj):
        """Get URL of the record's code repository."""
        relids = obj.get('metadata', {}).get('related_identifiers', [])

        def is_github_url(id):
            return (id['relation'] == 'isSupplementTo' and
                    id['scheme'] == 'url' and
                    id['identifier'].startswith('https://github.com'))
        # TODO: Strip 'tree/v1.0'?
        return next(
            (i['identifier'] for i in relids if is_github_url(i)), missing)


class Photograph(CreativeWork):
    """Marshmallow schema for schema.org/Photograph."""

    pass
