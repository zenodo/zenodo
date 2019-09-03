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

"""Zenodo Auditor for OAI-PMH."""

from __future__ import absolute_import, print_function, unicode_literals

from itertools import chain

from elasticsearch_dsl import Q
from flask import current_app
from invenio_cache import current_cache
from invenio_communities.models import Community
from invenio_db import db
from invenio_oaiserver.models import OAISet
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.models import RecordMetadata
from invenio_search import RecordsSearch
from mock import patch
from sickle import Sickle

from .api import Audit, Check
from .utils import sickle_requests_get_mock


class OAIAudit(Audit):
    """OAI Audit."""

    def __init__(self, audit_id, logger, communities):
        """Initialize an OAI audit."""
        super(OAIAudit, self).__init__(audit_id, logger)

        self._build_oai_sets_from_db()
        self._checks = chain(iter((OAICorrespondenceCheck(),)),
                             (OAISetResultCheck(self, c) for c in communities))

    def _build_oai_sets_from_db(self):
        # NOTE: We're relying on Redis-specific data types and commands, so we
        # have to be sure that we have Redis as our cache type.
        if current_app.config.get('CACHE_TYPE') != 'redis':
            raise Exception('OAIAudit: Redis cache type required.')

        self.cache = current_cache.cache._write_client
        self.cache_prefix = 'zenodo.auditor.oai:{}'.format(str(self.audit_id))

        record_oai_sets = (
            db.session.query(RecordMetadata)
            .join(
                PersistentIdentifier,
                RecordMetadata.id == PersistentIdentifier.object_uuid)
            .filter(
                PersistentIdentifier.pid_type == 'oai',
                PersistentIdentifier.status == PIDStatus.REGISTERED)
            .with_entities(
                PersistentIdentifier.pid_value,
                RecordMetadata.json)
        )

        for oai_id, record in record_oai_sets:
            for s in record.get('_oai', {}).get('sets', []):
                oai_control_number = oai_id.split(':')[-1]
                self.cache.sadd('{}:{}'.format(self.cache_prefix, s),
                                oai_control_number)

    def pop_db_oai_set(self, oai_set):
        """Return and remove from cache an OAI Set."""
        key = '{}:{}'.format(self.cache_prefix, oai_set)
        # TODO: Remove map as it needs to be string
        oai_sets = set(map(int, self.cache.smembers(key)))
        self.cache.delete(key)
        return oai_sets

    def clear_db_oai_set_cache(self):
        """Clear all cached OAI Sets generated for this audit."""
        for key in self.cache.scan_iter('{}:*'.format(self.cache_prefix)):
            self.cache.delete(key)


class OAICorrespondenceCheck(Check):
    """OAI Global Check."""

    def sets_correspondence(self):
        """Check correspondence of Communities and their OAI Sets."""
        missing_oai_sets = []
        for c in Community.query.all():
            if not OAISet.query.filter_by(spec=c.oaiset_spec).count():
                missing_oai_sets.append(c.id)
        if missing_oai_sets:
            self.issues['missing_oai_set'] = missing_oai_sets

        missing_communities = []
        for s in OAISet.query.filter(OAISet.search_pattern.is_(None),
                                     OAISet.spec.startswith('user-')):
            if not Community.query.filter_by(id=s.spec[5:]).count():
                missing_communities.append(s.spec)
        if missing_communities:
            self.issues['missing_community'] = missing_communities

    def perform(self):
        """Perform OAI Set correspondence checks."""
        self.sets_correspondence()


class OAISetResultCheck(Check):
    """OAI Set Count check."""

    def __init__(self, audit, community):
        """Initialize an OAI Set result check."""
        super(OAISetResultCheck, self).__init__()
        self.audit = audit
        self.community = community

    def results_consistency(self):
        """Check for consistent Community OAI Set results.

        There are three points of reference for OAI Set data:
          - Database Records
          - Elasticsearch Records Index
          - The `/oai2d` Endpoint

        Checking that the set of identifiers is consistent throughout these
        sources is vital.
        """
        db_ids = self._db_identifiers()
        es_ids = self._es_identifiers()
        oai2d_ids = self._oai2d_endpoint_identifiers()

        all_ids = (db_ids | es_ids | oai2d_ids)
        for source, ids in zip(('db', 'es', 'oai2d'),
                               (db_ids, es_ids, oai2d_ids)):
            missing_ids = list(all_ids - ids)
            if missing_ids:
                self.issues['missing_ids'][source] = missing_ids

    def _db_identifiers(self):
        """Return a set of the Community OAI Set recids from the database."""
        return self.audit.pop_db_oai_set(self.community.oaiset_spec)

    def _es_identifiers(self):
        """Return a set of the Community OAI Set recids from Elasticsearch."""
        query = Q('bool',
                  filter=Q('exists', field='_oai.id'),
                  must=Q('match', **{'_oai.sets': self.community.oaiset_spec}))
        index = current_app.config['OAISERVER_RECORD_INDEX']
        fields = ['_oai.id']
        search = RecordsSearch(index=index).fields(fields).query(query)
        return {int(r.meta.fields['_oai.id'][0].rsplit(':', 1)[-1])
                for r in search.scan()}

    def _oai2d_endpoint_identifiers(self):
        """Return a set of the Community OAI Set recids from OAI endpoint."""
        with patch('sickle.app.requests.get', new=sickle_requests_get_mock()):
            sickle = Sickle('http://auditor/oai2d')
            ids = sickle.ListIdentifiers(set=self.community.oaiset_spec,
                                         metadataPrefix='oai_dc')
            return {int(i.identifier.rsplit(':', 1)[-1]) for i in ids}

    def perform(self):
        """Perform OAI Set result checks."""
        self.results_consistency()

    def dump(self):
        """Dump OAI Set result check."""
        community_data = {
            'id': self.community.id,
            'oaiset_spec': self.community.oaiset_spec,
        }
        result = super(OAISetResultCheck, self).dump()
        result.update({'community': community_data})
        return result
