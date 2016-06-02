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

"""Deposit API."""

from __future__ import absolute_import

from invenio_deposit.api import Deposit
from invenio_communities.models import Community, InclusionRequest


class ZenodoDeposit(Deposit):
    """Define API for changing deposit state."""

    @staticmethod
    def _create_inclusion_requests(comm_ids, record):
        """Create inclusion requests for communities.

        :param comm_ids: Community IDs for which the inclusion requests might
                         should be created (if they don't exist already).
        :type comm_ids: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        for comm_id in comm_ids:
            comm = Community.get(comm_id)
            if not InclusionRequest.get(comm_id, record.id):
                InclusionRequest.create(comm, record)

    @staticmethod
    def _remove_accepted_communities(comm_ids, record):
        """Remove accepted communities.

        :param comm_ids: Already accepted community IDs which no longer
                         should have this record.
        :type comm_ids: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        for comm_id in comm_ids:
            comm = Community.get(comm_id)
            if comm.has_record(record):
                comm.remove_record(record)
        return record

    @staticmethod
    def _remove_obsolete_irs(comm_ids, record):
        """Remove obsolete inclusion requests.

        :param comm_ids: Community IDs as declared in deposit. Used to retire
                         obsolete inclusion requests.
        :type comm_ids: list of str
        :param record: Record corresponding to this deposit.
        :type record: `invenio_records.api.Record`
        """
        InclusionRequest.get_by_record(record.id).filter(
            InclusionRequest.id_community.notin_(comm_ids)).delete(
                synchronize_session='fetch')

    def _prepare_edit(self, record):
        """Prepare deposit for editing."""
        data = super(ZenodoDeposit, self)._prepare_edit(record)
        data.setdefault('communities', []).extend(
            [c.id_community for c in
             InclusionRequest.get_by_record(record.id)])
        data['communities'] = sorted(list(set(data['communities'])))
        if not data['communities']:
            del data['communities']
        return data

    def _publish_new(self, id_=None):
        """Publish new deposit with communities handling."""
        if 'communities' in self:
            # pop the 'communities' entry for record creation
            communities = self.pop('communities')
            record = super(ZenodoDeposit, self)._publish_new(id_=id_)
            self['communities'] = communities
            self._create_inclusion_requests(communities, record)
            return record
        else:
            return super(ZenodoDeposit, self)._publish_new(id_=id_)

    def _publish_edited(self):
        """Publish the edited deposit with communities merging."""
        pid, record = self.fetch_published()
        dep_comms = self.get('communities', [])
        rec_comms = record.get('communities', [])
        removals = set(rec_comms) - set(dep_comms)
        self._remove_accepted_communities(removals, record)
        additions = set(dep_comms) - set(rec_comms)
        self._create_inclusion_requests(additions, record)
        self._remove_obsolete_irs(dep_comms, record)
        new_rec_comms = sorted(list(set(dep_comms) & set(rec_comms)))
        record = super(ZenodoDeposit, self)._publish_edited()
        record['communities'] = new_rec_comms
        if not record['communities']:
            del record['communities']
        return record
