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

"""Zenodo Auditor for records."""

from invenio_accounts.models import User
from invenio_communities.models import Community
from invenio_oaiserver.models import OAISet
from invenio_pidstore.models import PersistentIdentifier
from jsonschema import SchemaError, ValidationError
from werkzeug.utils import cached_property

from .api import Audit, Check
from .utils import duplicates


class RecordAudit(Audit):
    """Record Audit."""

    def __init__(self, audit_id, logger, records):
        """Initialize a Record audit."""
        super(RecordAudit, self).__init__(audit_id, logger)
        self._checks = (RecordCheck(self, r) for r in records)

    @cached_property
    def all_communities(self):
        """Set of all the existing community identifiers."""
        return {c.id for c in Community.query.all()}

    @cached_property
    def all_owners(self):
        """Set of all the existing owner identifiers."""
        return {c.id for c in User.query.all()}

    @cached_property
    def custom_oai_sets(self):
        """Set of OAI sets that follow a record search pattern."""
        oai_sets = OAISet.query.filter(OAISet.search_pattern.isnot(None)).all()
        return {o.spec for o in oai_sets}

    @cached_property
    def all_oai_pids(self):
        """Set of OAI identifiers."""
        oai_pids = (PersistentIdentifier.query
                    .filter(PersistentIdentifier.pid_type == 'oai')
                    .all())
        return {p.pid_value for p in oai_pids}


class RecordCheck(Check):
    """Record Check."""

    def __init__(self, audit, record):
        """Initialize a Record check."""
        super(RecordCheck, self).__init__()
        self.audit = audit
        self.record = record

    def communities(self):
        """Check communities."""
        self._unresolvable_communities()
        self._duplicate_communities()

    def _unresolvable_communities(self):
        comms = set(self.record.get('communities', []))
        unresolvable_communities = comms - self.audit.all_communities
        if unresolvable_communities:
            self.issues['communities']['unresolvable'] = \
                list(unresolvable_communities)

    def _duplicate_communities(self):
        duplicate_comms = duplicates(self.record.get('communities', []))
        if duplicate_comms:
            self.issues['communities']['duplicates'] = duplicate_comms

    def owners(self):
        """Check owners."""
        self._duplicate_owners()
        self._unresolvable_owners()

    def _duplicate_owners(self):
        duplicate_owners = duplicates(self.record.get('owners', []))
        if duplicate_owners:
            self.issues['owners']['duplicates'] = duplicate_owners

    def _unresolvable_owners(self):
        owners = set(self.record.get('owners', []))
        unresolvable_owners = owners - self.audit.all_owners
        if unresolvable_owners:
            self.issues['owners']['unresolvable'] = list(unresolvable_owners)

    def files(self):
        """Check files."""
        self._duplicate_files()
        self._missing_files()
        self._multiple_buckets()
        self._bucket_mismatch()

    def _duplicate_files(self):
        files = self.record.get('_files', [])
        duplicate_keys = duplicates([f['key'] for f in files])
        duplicate_version_ids = duplicates([f['version_id'] for f in files])
        duplicate_files = [f for f in files
                           if (f['key'] in duplicate_keys or
                               f['version_id'] in duplicate_version_ids)]
        if duplicate_files:
            self.issues['files']['duplicates'] = duplicate_files

    def _missing_files(self):
        files = self.record.get('_files', [])
        if not files:
            self.issues['files']['missing'] = True

    def _multiple_buckets(self):
        files = self.record.get('_files', [])
        buckets = {f['bucket'] for f in files}
        if len(buckets) > 1:
            self.issues['files']['multiple_buckets'] = list(buckets)

    def _bucket_mismatch(self):
        """Check if buckets in '_files' don't match the ones '_buckets'."""
        files = self.record.get('_files', [])
        record_bucket = self.record.get('_buckets', {}).get('record')
        bucket_mismatch = [f for f in files if f['bucket'] != record_bucket]
        if bucket_mismatch:
            self.issues['files']['bucket_mismatch'] = bucket_mismatch

    def grants(self):
        """Check grants."""
        self._duplicate_grants()

    def _duplicate_grants(self):
        grant_ids = [g.get('$ref')
                     for g in self.record.get('grants', [])]
        duplicate_grants = duplicates(grant_ids)
        if any(duplicate_grants):
            self.issues['grants']['duplicates'] = duplicate_grants

    def oai(self):
        """Check OAI data."""
        self._oai_required()
        self._oai_non_minted_pid()
        self._oai_duplicate_sets()
        self._oai_community_correspondence()

    def _oai_required(self):
        oai_data = self.record.get('_oai', {})
        if not oai_data.get('id'):
            self.issues['oai']['missing']['id'] = True
        if not oai_data.get('updated'):
            self.issues['oai']['missing']['updated'] = True

    def _oai_non_minted_pid(self):
        oai_data = self.record.get('_oai', {})
        oai_pid = oai_data.get('id')
        if oai_pid and oai_pid not in self.audit.all_oai_pids:
            self.issues['oai']['non_minted_pid'] = oai_data.get('id')

    def _oai_duplicate_sets(self):
        oai_sets = self.record.get('_oai', {}).get('sets', [])
        duplicate_oai_sets = duplicates(oai_sets)
        if duplicate_oai_sets:
            self.issues['oai']['duplicate_oai_sets'] = duplicate_oai_sets

    def _oai_community_correspondence(self):
        oai_sets = set(self.record.get('_oai', {}).get('sets', []))
        comms = set(self.record.get('communities', []))
        if oai_sets or comms:
            comm_oai_sets = {s for s in oai_sets
                             if (s.startswith('user-') and
                                 s not in self.audit.custom_oai_sets)}

            comm_specs = {u'user-{c}'.format(c=c) for c in comms}
            missing_comm_oai_sets = comm_specs - comm_oai_sets
            if missing_comm_oai_sets:
                self.issues['oai']['missing_oai_sets'] = \
                    list(missing_comm_oai_sets)
            redundant_oai_sets = comm_oai_sets - comm_specs
            if redundant_oai_sets:
                self.issues['oai']['redundant_oai_sets'] = \
                    list(redundant_oai_sets)

    def jsonschema(self):
        """Check JSONSchema."""
        try:
            self.record.validate()
        except (ValidationError, SchemaError) as e:
            self.issues['jsonschema'] = str(e.message)

    def perform(self):
        """Perform record checks."""
        self.jsonschema()
        self.communities()
        self.files()
        self.owners()
        self.grants()
        self.oai()

    def dump(self):
        """Dump record check."""
        record_data = {
            'recid': self.record['recid'],
            'object_uuid': str(self.record.id),
        }
        result = super(RecordCheck, self).dump()
        result.update({'record': record_data})
        return result
