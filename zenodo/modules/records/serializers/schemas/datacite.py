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

"""Record serialization."""

from __future__ import absolute_import, print_function

import json

import arrow
from marshmallow import Schema, fields

from ...models import ObjectType


class IdentifierSchema(Schema):
    """Identifier schema."""

    identifier = fields.Function(lambda o: o)
    identifierType = fields.Constant('DOI')


class PersonSchema(Schema):
    """Creator/contributor common schema."""

    affiliation = fields.Str()
    nameIdentifier = fields.Method('get_nameidentifier')

    def get_nameidentifier(self, obj):
        """Get name identifier."""
        if obj.get('orcid'):
            return {
                "nameIdentifier": obj.get('orcid'),
                "nameIdentifierScheme": "ORCID",
                "schemeURI": "http://orcid.org/"
            }
        if obj.get('gnd'):
            return {
                "nameIdentifier": obj.get('gnd'),
                "nameIdentifierScheme": "GND",
            }
        return {}


class CreatorSchema(PersonSchema):
    """Creator schema."""

    creatorName = fields.Str(attribute='name')


class ContributorSchema(PersonSchema):
    """Contributor schema."""

    contributorName = fields.Str(attribute='name')
    contributorType = fields.Str(attribute='type')


class TitleSchema(Schema):
    """Title schema."""

    title = fields.Str(attribute='title')


class DateSchema(Schema):
    """Date schema."""

    date = fields.Str(attribute='date')
    dateType = fields.Str(attribute='type')


class AlternateIdentifierSchema(Schema):
    """Alternate identifiers schema."""

    alternateIdentifier = fields.Str(attribute='identifier')
    alternateIdentifierType = fields.Str(attribute='scheme')


class RelatedIdentifierSchema(Schema):
    """Alternate identifiers schema."""

    relatedIdentifier = fields.Str(attribute='identifier')
    relatedIdentifierType = fields.Method('get_type')
    relationType = fields.Function(
        lambda o: o['relation'][0].upper() + o['relation'][1:])

    def get_type(self, obj):
        """Get type."""
        if obj['scheme'] == 'handle':
            return 'Handle'
        elif obj['scheme'] == 'ads':
            return 'bibcode'
        elif obj['scheme'] == 'arxiv':
            return 'arXiv'
        else:
            return obj['scheme'].upper()


class DataCiteSchemaV1(Schema):
    """Schema for records v1 in JSON."""

    identifier = fields.Nested(IdentifierSchema, attribute='metadata.doi')
    creators = fields.List(
        fields.Nested(CreatorSchema),
        attribute='metadata.creators')
    titles = fields.List(
        fields.Nested(TitleSchema),
        attribute='metadata.title')
    publisher = fields.Constant('Zenodo')
    publicationYear = fields.Function(
        lambda o: str(arrow.get(o['metadata']['publication_date']).year))
    subjects = fields.Method('get_subjects')
    contributors = fields.Method('get_contributors')
    dates = fields.Method('get_dates')
    language = fields.Str(attribute='metadata.language')
    resourceType = fields.Method('get_type')
    alternateIdentifiers = fields.List(
        fields.Nested(AlternateIdentifierSchema),
        attribute='metadata.alternate_identifiers',
    )
    relatedIdentifiers = fields.Method('get_related_identifiers')
    rightsList = fields.Method('get_rights')
    descriptions = fields.Method('get_descriptions')

    def get_descriptions(self, obj):
        """."""
        items = []
        desc = obj['metadata']['description']
        if desc:
            items.append({
                'description': desc,
                'descriptionType': 'Abstract'

            })
        notes = obj['metadata'].get('notes')
        if notes:
            items.append({
                'description': notes,
                'descriptionType': 'Other'

            })
        refs = obj['metadata'].get('references')
        if refs:
            items.append({
                'description': json.dumps({
                    'references': [
                        r['raw_reference'] for r in refs
                        if 'raw_reference' in r]
                }),
                'descriptionType': 'Other'

            })
        return items

    def get_rights(self, obj):
        """Get rights."""
        items = []

        # license
        license_url = obj['metadata'].get('license', {}).get('url')
        license_text = obj['metadata'].get('license', {}).get('title')
        if license_url and license_text:
            items.append({
                'rightsURI': license_url,
                'rights': license_text,
            })

        # info:eu-repo
        items.append({
            'rightsURI': 'info:eu-repo/semantics/{}Access'.format(
                obj['metadata']['access_right']),
            'rights': '{0} access'.format(
                obj['metadata']['access_right']).title()
        })
        return items

    def get_type(self, obj):
        """Resource type."""
        t = ObjectType.get_by_dict(obj['metadata']['resource_type'])
        return {
            'resourceTypeGeneral': t['datacite']['general'],
            'resourceType': t['datacite'].get('type'),
        }

    def get_related_identifiers(self, obj):
        """Resource type."""
        accepted_types = [
            'doi', 'ark', 'ean13', 'eissn', 'handle', 'isbn', 'issn', 'istc',
            'lissn', 'lsid', 'purl', 'upc', 'url', 'urn', 'ads', 'arxiv',
            'bibcode',
        ]
        s = RelatedIdentifierSchema()

        items = []
        for r in obj['metadata'].get('related_identifiers', []):
            if r['scheme'] in accepted_types:
                items.append(s.dump(r).data)
        return items

    def get_subjects(self, obj):
        """Get subjects."""
        items = []
        for s in obj['metadata'].get('keywords', []):
            items.append({'subject': s})

        for s in obj['metadata'].get('subjects', []):
            items.append({
                'subject': s['identifier'],
                'subjectScheme': s['scheme'],
            })

        return items

    def get_dates(self, obj):
        """Get dates."""
        s = DateSchema()

        if obj['metadata']['access_right'] == 'embargoed' and \
                obj['metadata'].get('embargo_date'):
            return [
                s.dump(dict(
                    date=obj['metadata']['embargo_date'],
                    type='Available')).data,
                s.dump(dict(
                    date=obj['metadata']['publication_date'],
                    type='Accepted')).data,
            ]
        else:
            return [s.dump(dict(
                date=obj['metadata']['publication_date'],
                type='Issued')).data, ]

    def get_contributors(self, obj):
        """Get contributors."""
        def inject_type(c):
            c['type'] = 'Supervisor'
            return c

        # Contributors and supervisors
        s = ContributorSchema()
        contributors = obj['metadata'].get('contributors', [])
        contributors.extend([
            inject_type(c) for c in
            obj['metadata'].get('thesis_supervisors', [])
        ])

        items = []
        for c in contributors:
            items.append(s.dump(c).data)

        # Grants
        s = ContributorSchema()
        for g in obj['metadata'].get('grants', []):
            funder = g.get('funder', {}).get('name')
            eurepo = g.get('identifiers', {}).get('eurepo')
            if funder and eurepo:
                items.append({
                    'contributorName': funder,
                    'contributorType': 'Funder',
                    'nameIdentifier': {
                        'nameIdentifier': eurepo,
                        'nameIdentifierScheme': 'info',
                    },
                })

        return items
