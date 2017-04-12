# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

"""Deposit API."""

from __future__ import absolute_import

from contextlib import contextmanager
from copy import copy

from flask import current_app
from invenio_communities.models import Community, InclusionRequest
from invenio_db import db
from invenio_deposit.api import Deposit, preserve
from invenio_deposit.utils import mark_as_action
from invenio_files_rest.models import Bucket, MultipartObject, Part
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.models import RecordsBuckets

from zenodo.modules.communities.api import ZenodoCommunity
from zenodo.modules.records.api import ZenodoFileObject, ZenodoFilesIterator, \
    ZenodoRecord
from zenodo.modules.records.minters import is_local_doi, zenodo_doi_updater
from zenodo.modules.records.utils import is_doi_locally_managed
from zenodo.modules.sipstore.api import ZenodoSIP
from invenio_pidrelations.contrib.records import index_siblings

from .errors import MissingCommunityError, MissingFilesError, \
    OngoingMultipartUploadError
from .fetchers import zenodo_deposit_fetcher
from .minters import zenodo_deposit_minter

PRESERVE_FIELDS = (
    '_deposit',
    '_buckets',
    '_files',
    '_internal',
    '_oai',
    'relations',
    'owners',
    'recid',
    'conceptrecid',
    'conceptdoi',
)
"""Fields which will not be overwritten on edit."""


class ZenodoDeposit(Deposit):
    """Define API for changing deposit state."""

    file_cls = ZenodoFileObject

    files_iter_cls = ZenodoFilesIterator

    published_record_class = ZenodoRecord

    deposit_fetcher = staticmethod(zenodo_deposit_fetcher)

    deposit_minter = staticmethod(zenodo_deposit_minter)

    @property
    def multipart_files(self):
        """Get all multipart files."""
        return MultipartObject.query_by_bucket(self.files.bucket)

    def is_published(self):
        """Check if deposit is published."""
        return self['_deposit'].get('pid') is not None

    def has_minted_doi(self):
        """Check if deposit has a minted DOI."""
        return is_local_doi(self['doi']) if self.is_published() else False

    @staticmethod
    def _create_inclusion_requests(comms, record):
        """Create inclusion requests for communities.

        :param comms: Community IDs for which the inclusion requests might
                      should be created (if they don't exist already).
        :type comms: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        for comm_id in comms:
            comm_api = ZenodoCommunity(comm_id)
            # Check if InclusionRequest exists for any version already
            pending_irs = comm_api.get_comm_irs(record)
            if pending_irs.count() == 0 and not comm_api.has_record(record):
                comm = Community.get(comm_id)
                InclusionRequest.create(comm, record)

    @staticmethod
    def _remove_obsolete_irs(comms, record):
        """Remove obsolete inclusion requests.

        :param comms: Community IDs as declared in deposit. Used to remove
                      obsolete inclusion requests.
        :type comms: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """

        pid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=pid)
        sq = pv.children.with_entities(
            PersistentIdentifier.object_uuid).subquery()
        db.session.query(InclusionRequest).filter(
            InclusionRequest.id_record.in_(sq),
            InclusionRequest.id_community.notin_(comms)).delete(
                synchronize_session='fetch')

    def _prepare_edit(self, record):
        """Prepare deposit for editing.

        Extend the deposit's communities metadata by the pending inclusion
        requests.
        """
        data = super(ZenodoDeposit, self)._prepare_edit(record)
        data.setdefault('communities', []).extend(
            [c.id_community for c in
             InclusionRequest.get_by_record(record.id)])
        data['communities'] = sorted(list(set(data['communities'])))
        if not data['communities']:
            del data['communities']
        return data

    @staticmethod
    def _get_synced_oaisets(rec_comms):
        """Sync oaiset specs with communities in the record.

        This is necessary as not all communities modifications go through
        Community.add_record/remove_record API, hence OAISet can be left
        outdated.
        """
        fmt = current_app.config['COMMUNITIES_OAI_FORMAT']
        new_c_sets = [fmt.format(community_id=c) for c in rec_comms]
        return new_c_sets

        # TODO:
        # record['_oai']['updated'] = datetime_to_datestamp(datetime.utcnow())

    @staticmethod
    def _sync_oaisets_with_communities(record):
        """Sync oaiset specs with communities in the record.

        This is necessary as not all communities modifications go through
        Community.add_record/remove_record API, hence OAISet can be left
        outdated.
        """
        if current_app.config['COMMUNITIES_OAI_ENABLED']:
            from invenio_oaiserver.models import OAISet
            comms = record.get('communities', [])
            oai_sets = record['_oai'].get('sets', [])
            c_sets = [s for s in oai_sets if s.startswith('user-') and
                      not OAISet.query.filter_by(spec=s).one().search_pattern]
            fmt = current_app.config['COMMUNITIES_OAI_FORMAT']
            new_c_sets = [fmt.format(community_id=c) for c in comms]
            removals = set(c_sets) - set(new_c_sets)
            additions = set(new_c_sets) - set(c_sets)
            for s in removals:
                oaiset = OAISet.query.filter_by(spec=s).one()
                oaiset.remove_record(record)
            for s in additions:
                oaiset = OAISet.query.filter_by(spec=s).one()
                oaiset.add_record(record)
        return record

    def _filter_by_owned_communities(self, comms):
        """Filter the list of communities for auto accept.

        :param comms: Community IDs to be filtered by the deposit owners.
        :type comms: list of str
        :returns: Community IDs, which are owned by one of the deposit owners.
        :rtype: list
        """
        return [c for c in comms if Community.get(c).id_user in
                self['_deposit']['owners']]

    def _get_auto_requested(self, record):
        """Get communities which are to be auto-requested to each record."""
        if not current_app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']:
            return []
        comms = copy(current_app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'])
        pid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=pid)
        rec_grants = [ZenodoRecord.get_record(
            p.get_assigned_object()).get('grants') for p in pv.children]
        if self.get('grants') or any(rec_grants):
            comms.extend(
                current_app.config['ZENODO_COMMUNITIES_REQUEST_IF_GRANTS'])
        return comms

    def _get_auto_added(self, record):
        """Get communities which are to be auto added to each record."""
        if not current_app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']:
            return []
        comms = []
        pid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=pid)
        rec_grants = [ZenodoRecord.get_record(
            p.get_assigned_object()).get('grants') for p in pv.children]
        if self.get('grants') or any(rec_grants):
            comms = copy(current_app.config[
                'ZENODO_COMMUNITIES_ADD_IF_GRANTS'])
        return comms

    @staticmethod
    def _autoadd_versioning_related_identifiers(record):
        """Add versioning related identifiers."""
        conceptdoi = record.get('conceptdoi')
        if conceptdoi:
            pv = PIDVersioning(child=record.pid)
            siblings = pv.children.all()
            pid_index = siblings.index(record.pid)
            index_pids = siblings[(pid_index - 1):(pid_index + 2)]

            related_identifiers = record.get('related_identifiers')
            version_related_identifiers = [
                {'identifier': conceptdoi, 'scheme': 'doi', 'relation': 'isPartOf'},
                {'identifier': conceptdoi, 'scheme': 'doi', 'relation': 'isNewVersionOf'},
                {'identifier': conceptdoi, 'scheme': 'doi', 'relation': 'isPreviousVersionOf'},
            ]
            for ri in version_related_identifiers:
                if ri not in related_identifiers:
                    related_identifiers.append(ri)
            record['related_identifiers'] = related_identifiers
        return record

    @contextmanager
    def _process_files(self, record_id, data):
        """Snapshot bucket and add files in record during first publishing."""
        if self.files:
            assert not self.files.bucket.locked
            self.files.bucket.locked = True
            snapshot = self.files.bucket.snapshot(lock=True)
            data['_files'] = self.files.dumps(bucket=snapshot.id)
            data['_buckets']['record'] = str(snapshot.id)
            yield data
            db.session.add(RecordsBuckets(
                record_id=record_id, bucket_id=snapshot.id
            ))
        else:
            yield data

    def _get_new_communities(self, dep_comms, rec_comms, record):
        # New communities, which should be added automatically
        owned_comms = set(self._filter_by_owned_communities(dep_comms))

        # Communities which are to be added to every published record
        auto_added = set(self._get_auto_added(record))

        new_rec_comms = (dep_comms & rec_comms) | owned_comms | auto_added

        auto_requested = set(self._get_auto_requested(record))

        # New communities, for which the InclusionRequests should be made
        new_ir_comms = (dep_comms - new_rec_comms) | auto_requested

        new_dep_comms = new_rec_comms | new_ir_comms

        return new_dep_comms, new_rec_comms, new_ir_comms

    def _sync_communities(self, dep_comms, rec_comms, record):
        new_dep_comms, new_rec_comms, new_ir_comms = \
            self._get_new_communities(dep_comms, rec_comms, record)

        # Update Communities and OAISet information for all record versions
        recid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=recid)
        for pid in pv.children:
            if pid != recid:
                rec = ZenodoRecord.get_record(pid.get_assigned_object())
                rec['communities'] = sorted(new_rec_comms)
                if current_app.config['COMMUNITIES_OAI_ENABLED']:
                    rec = self._sync_oaisets_with_communities(rec)
                if not rec['communities']:
                    del rec['communities']
                rec.commit()
                depid = PersistentIdentifier.get(
                    'depid', rec['_deposit']['id'])
                deposit = ZenodoDeposit.get_record(depid.get_assigned_object())
                deposit['communities'] = sorted(new_dep_comms)
                if not deposit['communities']:
                    del deposit['communities']
                deposit.commit()

        # Update new version deposit
        if pv.draft_child_deposit:
            draft_dep = ZenodoDeposit.get_record(
                pv.draft_child_deposit.get_assigned_object())
            if draft_dep.id != self.id:
                draft_dep['communities'] = sorted(new_dep_comms)
                if not draft_dep['communities']:
                    del draft_dep['communities']
                draft_dep.commit()

        record['communities'] = sorted(new_rec_comms)
        if current_app.config['COMMUNITIES_OAI_ENABLED']:
            record = self._sync_oaisets_with_communities(record)
        if not record['communities']:
            del record['communities']

        self['communities'] = sorted(new_dep_comms)
        if not self['communities']:
            del self['communities']

        # Create Inclusion requests against this record
        self._create_inclusion_requests(new_ir_comms, record)

        # Remove obsolete InclusionRequests again the record and its versions
        self._remove_obsolete_irs(new_ir_comms, record)

        return record

    def _publish_new(self, id_=None):
        """Publish new deposit with communities handling."""
        dep_comms = set(self.pop('communities', []))
        record = super(ZenodoDeposit, self)._publish_new(id_=id_)
        recid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=recid)
        if pv.children.count() > 1:
            prev_recid = pv.children.all()[-2]
            rec_comms = set(ZenodoRecord.get_record(
                prev_recid.get_assigned_object()).get('communities', []))
        else:
            rec_comms = set()

        record = self._sync_communities(dep_comms, rec_comms, record)
        record.commit()

        return record

    def _publish_edited(self):
        """Publish the edited deposit with communities merging."""
        dep_comms = set(self.get('communities', []))
        pid, record = self.fetch_published()
        rec_comms = set(record.get('communities', []))

        edited_record = super(ZenodoDeposit, self)._publish_edited()

        # Preserve some of the previously published record fields
        preserve_record_fields = ['_files', '_oai', '_buckets', '_internal']
        for k in preserve_record_fields:
            if k in record:
                edited_record[k] = record[k]

        zenodo_doi_updater(edited_record.id, edited_record)

        edited_record = self._sync_communities(dep_comms, rec_comms,
                                               edited_record)
        return edited_record

    def validate_publish(self):
        """Validate deposit."""
        super(ZenodoDeposit, self).validate()

        if len(self.files) == 0:
            raise MissingFilesError()

        if self.multipart_files.count() != 0:
            raise OngoingMultipartUploadError()

        if 'communities' in self:
            missing = [c for c in self['communities']
                       if Community.get(c) is None]
            if missing:
                raise MissingCommunityError(missing)

    @mark_as_action
    def publish(self, pid=None, id_=None, user_id=None, sip_agent=None):
        """Publish the Zenodo deposit."""
        self['owners'] = self['_deposit']['owners']
        self.validate_publish()
        is_first_publishing = not self.is_published()
        deposit = super(ZenodoDeposit, self).publish(pid, id_)
        pid, record = deposit.fetch_published()
        ZenodoSIP.create(pid, record, create_sip_files=is_first_publishing,
                         user_id=user_id, agent=sip_agent)
        return deposit

    @classmethod
    def create(cls, data, id_=None):
        """Create a deposit.

        Adds bucket creation immediately on deposit creation.
        """
        bucket = Bucket.create(
            quota_size=current_app.config['ZENODO_BUCKET_QUOTA_SIZE'],
            max_file_size=current_app.config['ZENODO_MAX_FILE_SIZE'],
        )
        data['_buckets'] = {'deposit': str(bucket.id)}
        deposit = super(ZenodoDeposit, cls).create(data, id_=id_)

        RecordsBuckets.create(record=deposit.model, bucket=bucket)
        return deposit

    @preserve(result=False, fields=PRESERVE_FIELDS)
    def clear(self, *args, **kwargs):
        """Clear only drafts."""
        super(ZenodoDeposit, self).clear(*args, **kwargs)

    @preserve(result=False, fields=PRESERVE_FIELDS)
    def update(self, *args, **kwargs):
        """Update only drafts."""
        super(ZenodoDeposit, self).update(*args, **kwargs)

    @preserve(fields=PRESERVE_FIELDS)
    def patch(self, *args, **kwargs):
        """Patch only drafts."""
        return super(ZenodoDeposit, self).patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete the deposit."""
        if self['_deposit'].get('pid'):
            raise PIDInvalidAction()

        # Delete reserved recid.
        pid_recid = PersistentIdentifier.get(
            pid_type='recid', pid_value=self['recid'])

        # TODO: might crash for legacy saved deposits
        versioning = PIDVersioning(child=pid_recid)
        if versioning.exists:
            from zenodo.modules.deposit.indexer import index_siblings
            draft_child = versioning.draft_child
            siblings = versioning.children.all()
            versioning.remove_draft_child()
            index_siblings(draft_child, siblings=siblings,
                           only_neighbors=True)

        if pid_recid.status == PIDStatus.RESERVED:
            db.session.delete(pid_recid)

        # Completely remove bucket
        q = RecordsBuckets.query.filter_by(record_id=self.id)
        bucket = q.one().bucket
        with db.session.begin_nested():
            # Remove Record-Bucket link
            q.delete()
            mp_q = MultipartObject.query_by_bucket(bucket)
            # Remove multipart objects
            Part.query.filter(
                Part.upload_id.in_(mp_q.with_entities(
                    MultipartObject.upload_id).subquery())
            ).delete(synchronize_session='fetch')
            mp_q.delete(synchronize_session='fetch')
        bucket.remove()


        return super(ZenodoDeposit, self).delete(*args, **kwargs)


    @mark_as_action
    def newversion(self, pid=None):
        """Create a new version deposit."""
        assert self.is_published()

        # Check that there is not a newer draft version for this record
        pid, record = self.fetch_published()
        pv = PIDVersioning(child=pid)
        if (not pv.draft_child and
                is_doi_locally_managed(record['doi'])):
            # Let's create the new version draft!
            with db.session.begin_nested():

                # Get copy of the record
                data = record.dumps()

                owners = data['_deposit']['owners']

                # TODO: Check other data that may need to be removed
                keys_to_remove = (
                    '_deposit', 'doi', '_oai', '_files', '_buckets', '$schema')
                for k in keys_to_remove:
                    data.pop(k, None)

                # NOTE: We call the superclass `create()` method, because we
                # don't want a new empty bucket, but an unlocked snapshot of
                # the old record's bucket.
                deposit = (super(ZenodoDeposit, self).create(data))
                # Injecting owners is required in case of creating new
                # version this outside of request context
                deposit['_deposit']['owners'] = owners

                pv = PIDVersioning(child=pid)
                index_siblings(pv.draft_child, only_neighbors=True)

                with db.session.begin_nested():
                    # Create snapshot from the record's bucket and update data
                    snapshot = record.files.bucket.snapshot(lock=False)
                    snapshot.locked = False
                # FIXME: `snapshot.id` might not be present because we need to
                # commit first to the DB.
                # db.session.commit()
                deposit['_buckets'] = {'deposit': str(snapshot.id)}
                RecordsBuckets.create(record=deposit.model, bucket=snapshot)
                deposit.commit()
        return self
