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

import uuid
from contextlib import contextmanager
from copy import copy, deepcopy

from flask import current_app
from invenio_communities.models import Community, InclusionRequest
from invenio_db import db
from invenio_deposit.api import Deposit, preserve
from invenio_deposit.utils import mark_as_action
from invenio_files_rest.models import Bucket, MultipartObject, Part
from invenio_pidstore.errors import PIDInvalidAction
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_files.models import RecordsBuckets
from invenio_pidrelations.contrib.records import get_latest_draft

from zenodo.modules.records.api import (ZenodoFileObject, ZenodoFilesIterator,
                                        ZenodoRecord)
from zenodo.modules.records.minters import is_local_doi, zenodo_doi_updater
from zenodo.modules.sipstore.api import ZenodoSIP

from .errors import (MissingCommunityError, MissingFilesError,
                     OngoingMultipartUploadError)
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
            comm = Community.get(comm_id)
            if not InclusionRequest.get(comm_id, record.id):
                InclusionRequest.create(comm, record)

    @staticmethod
    def _remove_accepted_communities(comms, record):
        """Remove accepted communities.

        :param comms: Already accepted community IDs which no longer
                      should have this record.
        :type comms: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        :returns: modified 'record' argument
        :rtype: `invenio_records.api.Record`
        """
        for comm_id in comms:
            comm = Community.get(comm_id)
            if comm.has_record(record):
                comm.remove_record(record)  # Handles oai-sets internally
        return record

    @staticmethod
    def _remove_obsolete_irs(comms, record):
        """Remove obsolete inclusion requests.

        :param comms: Community IDs as declared in deposit. Used to remove
                      obsolete inclusion requests.
        :type comms: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        InclusionRequest.get_by_record(record.id).filter(
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
    def _autoadd_communities(comms, record):
        """Add record to all communities ommiting the inclusion request.

        :param comms: Community IDs, to which the record should be added.
        :type comms: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        for comm_id in comms:
            comm = Community.get(comm_id)
            if not comm.has_record(record):
                comm.add_record(record)  # Handles oai-sets internally

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

    def _get_auto_requested(self):
        """Get communities which are to be auto-requested to each record."""
        if not current_app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']:
            return []
        comms = copy(current_app.config['ZENODO_COMMUNITIES_AUTO_REQUEST'])
        if self.get('grants'):
            comms.extend(
                current_app.config['ZENODO_COMMUNITIES_REQUEST_IF_GRANTS'])
        return comms

    def _get_auto_added(self):
        """Get communities which are to be auto added to each record."""
        if not current_app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']:
            return []
        comms = []
        if self.get('grants'):
            comms = copy(current_app.config[
                'ZENODO_COMMUNITIES_ADD_IF_GRANTS'])
        return comms

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

    def _publish_new(self, id_=None):
        """Publish new deposit with communities handling."""
        # pop the 'communities' entry so they aren't added to the Record
        dep_comms = set(self.pop('communities', []))

        # Communities for automatic acceptance
        owned_comms = set(self._filter_by_owned_communities(dep_comms))

        auto_added = set(self._get_auto_added())

        # Communities for which the InclusionRequest should be made
        # Exclude owned ones and auto added ones
        new_ir_comms = dep_comms - owned_comms - auto_added

        # Communities which are to be auto-requested to each published record
        auto_request = set(self._get_auto_requested())

        # Add the owned communities to the record
        # FIXME: This fails if the Community was added by the user...
        # May be unique case though if you are Zenodo admin (user 1)
        self._autoadd_communities(owned_comms | auto_added, self)

        record = super(ZenodoDeposit, self)._publish_new(id_=id_)

        self._create_inclusion_requests(new_ir_comms | auto_request, record)

        # Push the communities back (if any) so they appear in deposit
        self['communities'] = sorted(dep_comms | auto_added | auto_request)
        self._sync_oaisets_with_communities(record)
        if not self['communities']:  # No key rather than empty list
            del self['communities']
        return record

    def _publish_edited(self):
        """Publish the edited deposit with communities merging."""
        pid, record = self.fetch_published()
        dep_comms = set(self.get('communities', []))
        rec_comms = set(record.get('communities', []))

        # Already accepted communities which should be removed
        removals = rec_comms - dep_comms

        # New communities by user
        new_comms = dep_comms - rec_comms

        # New communities, which should be added automatically
        new_owned_comms = set(self._filter_by_owned_communities(new_comms))

        # Communities which are to be added to every published record
        auto_added = set(self._get_auto_added())

        # New communities, for which the InclusionRequests should be made
        new_ir_comms = new_comms - new_owned_comms - auto_added

        # Communities which are to be auto-requested to each published record
        auto_request = set(self._get_auto_requested()) - rec_comms

        self._remove_accepted_communities(removals, record)

        self._autoadd_communities(new_owned_comms | auto_added, record)
        self._create_inclusion_requests(new_ir_comms | auto_request, record)

        # Remove obsolete InclusionRequests
        self._remove_obsolete_irs(dep_comms | auto_request, record)

        # Communities, which should be in record after publishing:
        new_rec_comms = (dep_comms & rec_comms) | new_owned_comms | auto_added
        edited_record = super(ZenodoDeposit, self)._publish_edited()

        # Preserve some of the previously published record fields
        preserve_record_fields = ['_files', '_oai', '_buckets', '_internal']
        for k in preserve_record_fields:
            if k in record:
                edited_record[k] = record[k]

        # Add communities entry to deposit (self)
        self['communities'] = sorted(set(self.get('communities', [])) |
                                     auto_added | auto_request)
        if not self['communities']:
            del self['communities']

        # Add communities entry to record
        edited_record['communities'] = sorted(new_rec_comms)
        edited_record = self._sync_oaisets_with_communities(edited_record)
        if not edited_record['communities']:
            del edited_record['communities']
        zenodo_doi_updater(edited_record.id, edited_record)
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
        _, latest_draft = get_latest_draft(pid)
        if not latest_draft:
            # Let's create the new version draft!
            with db.session.begin_nested():

                # Get copy of the record
                data = record.dumps()

                # TODO: Check other data that may need to be removed
                keys_to_remove = (
                    '_deposit', 'doi', '_oai', '_files', '_buckets', '$schema')
                for k in keys_to_remove:
                    data.pop(k, None)

                # NOTE: We call the superclass `create()` method, because we don't
                # want a new empty bucket, but an unlocked snapshot of the old
                # record's bucket.
                deposit = (super(ZenodoDeposit, self).create(data))

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
