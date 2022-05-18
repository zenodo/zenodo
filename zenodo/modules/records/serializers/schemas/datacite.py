# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016-2018 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

import json

import arrow
import pycountry
from flask import current_app
from marshmallow import Schema, fields, missing, post_dump

from ...models import ObjectType
from ...utils import is_doi_locally_managed
from .common import ui_link_for


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

    title = fields.Str()


class DateSchema(Schema):
    """Date schema."""

    VALID_DATE_TYPES = {
        'Accepted',
        'Available',
        'Copyrighted',
        'Collected',
        'Created',
        'Issued',
        'Submitted',
        'Updated',
        'Valid',
    }

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
    resourceTypeGeneral = fields.Method(
        'get_resource_type', attribute='resource_type')

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

    def get_resource_type(self, obj):
        """Resource type."""
        resource_type = obj.get('resource_type')
        if resource_type:
            t = ObjectType.get_by_dict(resource_type)
            return t['datacite']['general']
        else:
            return missing


class DataCiteSchema(Schema):
    """Base class for schemas."""

    DATE_SCHEMA = DateSchema

    identifier = fields.Method('get_identifier', attribute='metadata.doi')
    titles = fields.List(fields.Nested(TitleSchema), attribute='metadata')
    publisher = fields.Constant('Zenodo')
    publicationYear = fields.Function(
        lambda o: str(arrow.get(o['metadata']['publication_date']).year))
    subjects = fields.Method('get_subjects')
    dates = fields.Method('get_dates')
    language = fields.Method('get_language')
    geoLocations = fields.Method('get_locations')
    version = fields.Str(attribute='metadata.version')
    resourceType = fields.Method('get_type')
    alternateIdentifiers = fields.List(
        fields.Nested(AlternateIdentifierSchema),
        attribute='metadata.alternate_identifiers',
    )
    relatedIdentifiers = fields.Method('get_related_identifiers')
    rightsList = fields.Method('get_rights')
    descriptions = fields.Method('get_descriptions')

    @post_dump
    def cleanup(self, data):
        """Clean the data."""
        # Remove the language if Alpha-2 code was not found
        if 'language' in data and data['language'] is None:
            del data['language']
        return data

    def get_identifier(self, obj):
        """Get record main identifier."""
        doi = obj['metadata'].get('doi', '')
        if is_doi_locally_managed(doi):
            return {
                'identifier': doi,
                'identifierType': 'DOI'
            }
        else:
            recid = obj.get('metadata', {}).get('recid', '')
            return {
                'identifier': ui_link_for('record_html', id=recid),
                'identifierType': 'URL',
            }

    def get_language(self, obj):
        """Export language to the Alpha-2 code (if available)."""
        lang = obj['metadata'].get('language', None)
        if lang:
            lang_res = pycountry.languages.get(alpha_3=lang)
            if not lang_res or not hasattr(lang_res, 'alpha_2'):
                return None
            return lang_res.alpha_2
        return None

    def get_descriptions(self, obj):
        """Get descriptions."""
        items = []
        desc = obj['metadata']['description']
        max_descr_size = current_app.config.get(
            'DATACITE_MAX_DESCRIPTION_SIZE', 20000)
        if desc:
            items.append({
                'description': desc[:max_descr_size],
                'descriptionType': 'Abstract'
            })
        notes = obj['metadata'].get('notes')
        if notes:
            items.append({
                'description': notes[:max_descr_size],
                'descriptionType': 'Other'
            })
        refs = obj['metadata'].get('references')
        if refs:
            items.append({
                'description': json.dumps({
                    'references': [
                        r['raw_reference'] for r in refs
                        if 'raw_reference' in r]
                })[:max_descr_size],
                'descriptionType': 'Other'
            })
        method = obj['metadata'].get('method')
        if method:
            items.append({
                'description': method[:max_descr_size],
                'descriptionType': 'Methods'
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
        type_ = {
            'resourceTypeGeneral': t['datacite']['general'],
            'resourceType': t['datacite'].get('type'),
        }
        oa_type = ObjectType.get_openaire_subtype(obj['metadata'])
        # NOTE: This overwrites the resourceType if the configuration
        # of the OpenAIRE subtypes overlaps with regular subtypes.
        if oa_type:
            type_['resourceType'] = oa_type
        return type_

    def get_related_identifiers(self, obj):
        """Related identifiers."""
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

        doi = obj['metadata'].get('doi', '')
        if not is_doi_locally_managed(doi):
            items.append(s.dump({
                'identifier': doi,
                'scheme': 'doi',
                'relation': 'IsIdenticalTo',
            }).data)

        # Zenodo community identifiers
        for comm in obj['metadata'].get('communities', []):
            items.append(s.dump({
                'identifier': ui_link_for('community', id=comm),
                'scheme': 'url',
                'relation': 'IsPartOf',
            }).data)

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
        """Get dates from record."""
        schema_cls = self.DATE_SCHEMA
        schema = schema_cls()
        dates = []
        if obj['metadata']['access_right'] == 'embargoed' and \
                obj['metadata'].get('embargo_date'):
            dates.append(schema.dump(dict(
                date=obj['metadata']['embargo_date'],
                type='Available')).data)

            dates.append(schema.dump(dict(
                date=obj['metadata']['publication_date'],
                type='Accepted')).data)
        else:
            dates.append(schema.dump(dict(
                date=obj['metadata']['publication_date'],
                type='Issued')).data)
        for interval in obj['metadata'].get('dates', []):
            date_type = interval.get('type')
            if date_type in schema.VALID_DATE_TYPES:
                start = interval.get('start') or ''
                end = interval.get('end') or ''
                if start != '' and end != '' and start == end:
                    dates.append(schema.dump(dict(
                        date=start,
                        type=date_type,
                        info=interval.get('description', missing))).data)
                else:
                    dates.append(schema.dump(dict(
                        date=start + '/' + end,
                        type=date_type,
                        info=interval.get('description', missing))).data)
        return dates


class DataCiteSchemaV1(DataCiteSchema):
    """Schema for records v1 in JSON."""

    creators = fields.List(
        fields.Nested(CreatorSchema),
        attribute='metadata.creators')

    contributors = fields.Method('get_contributors')

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

    def get_locations(self, obj):
        """Get locations."""
        locations = []
        for l in obj['metadata'].get('locations', []):
            location = {'geoLocationPlace': l['place']}
            if l.get('lat') and l.get('lon'):
                location['geoLocationPoint'] = '{} {}'\
                    .format(l['lat'], l['lon'])
            locations.append(location)
        return locations or missing

    def get_related_identifiers(self, obj):
        """Related identifiers."""
        items = super(DataCiteSchemaV1, self).get_related_identifiers(obj)
        for item in items:
            if item['relationType'] and item['relationType'] == 'IsVersionOf':
                item['relationType'] = 'IsPartOf'
            if item['relationType'] and item['relationType'] == 'HasVersion':
                item['relationType'] = 'HasPart'
        return items


class PersonSchemav4(Schema):
    """Creator/contributor common schema for v4."""

    affiliations = fields.List(
        fields.Str(),
        attribute='affiliation')

    nameIdentifiers = fields.Method('get_nameidentifiers')

    familyName = fields.Method('get_familyname')
    givenName = fields.Method('get_givennames')

    def get_familyname(self, obj):
        """Get family name."""
        name = obj.get('name')
        if name:
            names = name.split(',')
            if len(names) == 2:
                return names.pop(0).strip()
        return ''

    def get_givennames(self, obj):
        """Get given name."""
        name = obj.get('name')
        if name:
            names = name.split(',')
            if len(names) == 2:
                return names.pop(1).strip()
        return ''

    def get_nameidentifiers(self, obj):
        """Get name identifier."""
        name_identifiers = []
        if obj.get('orcid'):
            name_identifiers.append({
                "nameIdentifier": obj.get('orcid'),
                "nameIdentifierScheme": "ORCID",
                "schemeURI": "http://orcid.org/"
            })
        if obj.get('gnd'):
            name_identifiers.append({
                "nameIdentifier": obj.get('gnd'),
                "nameIdentifierScheme": "GND",
            })
        return name_identifiers


class CreatorSchemav4(PersonSchemav4):
    """Creator schema for v4."""

    creatorName = fields.Str(attribute='name')


class ContributorSchemav4(PersonSchemav4):
    """Contributor schema for v4."""

    contributorName = fields.Str(attribute='name')
    contributorType = fields.Str(attribute='type')


class DateSchemaV4(DateSchema):
    """Date schema for v4."""

    VALID_DATE_TYPES = {
        'Accepted',
        'Available',
        'Copyrighted',
        'Collected',
        'Created',
        'Issued',
        'Submitted',
        'Updated',
        'Valid',
        'Withdrawn',
        'Other',
    }

    dateInformation = fields.Str(attribute='info')


class DataCiteSchemaV4(DataCiteSchema):
    """Schema for records v4 in JSON."""

    DATE_SCHEMA = DateSchemaV4

    creators = fields.List(
        fields.Nested(CreatorSchemav4),
        attribute='metadata.creators')

    contributors = fields.Method('get_contributors')
    fundingReferences = fields.Method('get_fundingreferences')

    def get_contributors(self, obj):
        """Get contributors."""
        def inject_type(c):
            c['type'] = 'Supervisor'
            return c

        # Contributors and supervisors
        s = ContributorSchemav4()
        contributors = obj['metadata'].get('contributors', [])
        contributors.extend([
            inject_type(c) for c in
            obj['metadata'].get('thesis', {}).get('supervisors', [])
        ])

        items = []
        for c in contributors:
            items.append(s.dump(c).data)

        return items

    def get_fundingreferences(self, obj):
        """Get funding references."""
        items = []
        for g in obj['metadata'].get('grants', []):
            funder_name = g.get('funder', {}).get('name')
            funder_identifier = g.get('funder', {}).get('doi')
            award_number = g.get('code')
            award_title = g.get('title')

            eurepo = g.get('identifiers', {}).get('eurepo')
            if funder_name and eurepo:
                items.append({
                    'funderName': funder_name,
                    'funderIdentifier': {
                        'funderIdentifier': funder_identifier,
                        'funderIdentifierType': 'Crossref Funder ID',
                    },
                    'awardNumber': {
                        'awardNumber': award_number,
                        'awardURI': eurepo
                    },
                    'awardTitle': award_title
                })

        return items

    def get_locations(self, obj):
        """Get locations."""
        locations = []
        for l in obj['metadata'].get('locations', []):
            location = {'geoLocationPlace': l['place']}
            if l.get('lat') and l.get('lon'):
                location['geoLocationPoint'] = {
                         'pointLongitude': l['lon'],
                         'pointLatitude': l['lat']
                    }
            locations.append(location)
        return locations or missing
