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

import lxml.html
from marshmallow import Schema, fields

from zenodo.modules.openaire.helpers import openaire_community_identifier, \
    resolve_openaire_communities

from ...models import ObjectType


class DublinCoreV1(Schema):
    """Schema for records v1 in JSON."""

    identifiers = fields.Method('get_identifiers')
    titles = fields.Function(lambda o: [o['metadata'].get('title', u'')])
    creators = fields.Method('get_creators')
    relations = fields.Method('get_relations')
    rights = fields.Method('get_rights')
    dates = fields.Method('get_dates')
    subjects = fields.Method('get_subjects')
    descriptions = fields.Method('get_descriptions')
    publishers = fields.Method('get_publishers')
    contributors = fields.Method('get_contributors')
    types = fields.Method('get_types')
    sources = fields.Method('get_sources')
    languages = fields.Function(lambda o: [o['metadata'].get('language', u'')])

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = []
        items.append(u'https://zenodo.org/record/{0}'.format(
            obj['metadata']['recid']))
        items.append(obj['metadata'].get('doi', u''))
        oai = obj['metadata'].get('_oai', {}).get('id')
        if oai:
            items.append(oai)
        return items

    def get_creators(self, obj):
        """Get creators."""
        return [c['name'] for c in obj['metadata'].get('creators', [])]

    def get_relations(self, obj):
        """Get creators."""
        rels = []
        # Grants
        for g in obj['metadata'].get('grants', []):
            eurepo_id = g.get('identifiers', {}).get('eurepo')
            if eurepo_id:
                rels.append(eurepo_id)

        # Alternate identifiers
        for a in obj['metadata'].get('alternate_identifiers', []):
            rels.append(
                u'info:eu-repo/semantics/altIdentifier/{0}/{1}'.format(
                    a['scheme'],
                    a['identifier']))

        # Related identifiers
        for a in obj['metadata'].get('related_identifiers', []):
            rels.append(
                u'{0}:{1}'.format(
                    a['scheme'],
                    a['identifier']))

        # OpenAIRE community identifiers
        openaire_comms = resolve_openaire_communities(
            obj['metadata'].get('communities', []))
        for oa_comm in openaire_comms:
            rels.append(
                u'url:{0}'.format(openaire_community_identifier(oa_comm)))

        return rels

    def get_rights(self, obj):
        """Get rights."""
        rights = [
            u'info:eu-repo/semantics/{}Access'.format(
                obj['metadata']['access_right'])]
        license_url = obj['metadata'].get('license', {}).get('url')
        if license_url:
            rights.append(license_url)
        return rights

    def get_dates(self, obj):
        """Get dates."""
        dates = [obj['metadata']['publication_date']]
        if obj['metadata']['access_right'] == u'embargoed':
            dates.append(
                u'info:eu-repo/date/embargoEnd/{0}'.format(
                    obj['metadata']['embargo_date']))

        return dates

    def get_descriptions(self, obj):
        """Get descriptions."""
        descriptions = []
        if obj['metadata'].get('description', '').strip():
            descriptions.append(
                lxml.html.document_fromstring(obj['metadata']['description'])
                .text_content().replace(u"\xa0", u" "))
        return descriptions

    def get_subjects(self, obj):
        """Get subjects."""
        metadata = obj['metadata']
        subjects = []
        subjects.extend(metadata.get('keywords', []))
        subjects.extend((s['term'] for s in metadata.get('subjects', [])))
        return subjects

    def get_publishers(self, obj):
        """Get publishers."""
        imprint = obj['metadata'].get('imprint', {}).get('publisher')
        if imprint:
            return [imprint]
        part = obj['metadata'].get('part_of', {}).get('publisher')
        if part:
            return [part]
        return []

    def get_contributors(self, obj):
        """Get contributors."""
        return [c['name'] for c in obj['metadata'].get('contributors', [])]

    def get_types(self, obj):
        """Get types."""
        t = ObjectType.get_by_dict(obj['metadata']['resource_type'])
        types = [t['eurepo'], t['internal_id']]

        oa_type = ObjectType.get_openaire_subtype(obj['metadata'])
        if oa_type:
            types.append(oa_type)
        return types

    def get_sources(self, obj):
        """Get sources."""
        items = []

        # Journal
        journal = obj['metadata'].get('journal')
        if journal is not None:
            vol = journal.get('volume')
            issue = journal.get('issue')
            if vol and issue:
                vol = u'{0}({1})'.format(vol, issue)
            if vol is None:
                vol = issue

            y = journal.get('year')

            parts = [
                journal.get('title'),
                vol,
                journal.get('pages'),
                u'({0})'.format(y) if y else None,
            ]
            items.append(u' '.join([x for x in parts if x]))

        # Meetings
        m = obj['metadata'].get('meetings', {})
        if m:
            parts = [
                m.get('acronym'),
                m.get('title'),
                m.get('place'),
                m.get('dates'),
            ]
            items.append(', '.join([x for x in parts if x]))

        return items
