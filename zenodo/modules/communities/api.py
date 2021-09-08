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

"""Zenodo Communities API."""

from __future__ import absolute_import
from flask import after_this_request, request

from flask.globals import current_app
from invenio_communities.errors import InclusionRequestMissingError
from invenio_communities.models import Community, InclusionRequest
from invenio_db import db
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from six import string_types, text_type

from zenodo.modules.records.api import ZenodoRecord

from .signals import record_accepted


class ZenodoCommunity(object):
    """API class for Zenodo Communities."""

    def __init__(self, community):
        """Construct the API object.

        :param community: Instantiate the API with the community.
            Parameter can be either the model instance, or string
            (community ID).
        :type community: invenio_communities.model.Community or str
        """
        if isinstance(community, (text_type, string_types)):
            self.community = Community.get(community)
        else:
            self.community = community

    @staticmethod
    def get_irs(record, community_id=None, pid=None):
        """Get all inclusion requests for given record and community.

        :param record: record for which the inclusion requests are fetched.
            This includes all of the record's versions.
        :param community_id: Narrow down the query to given community.
            Query for all communities if 'None'.
        """
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])
        pv = PIDVersioning(child=pid)
        if pv.exists:
            sq = pv.children.with_entities(
                PersistentIdentifier.object_uuid).subquery()
            filter_cond = [
                InclusionRequest.id_record.in_(sq),
            ]
            if community_id:
                filter_cond.append(
                    InclusionRequest.id_community == community_id)
            q = (db.session.query(InclusionRequest).filter(*filter_cond))
        else:
            q = InclusionRequest.query.filter_by(id_record=record.id).order_by(
                InclusionRequest.id_community)
        return q

    def get_comm_irs(self, record, pid=None):
        """Inclusion requests for record's versions made to this community.

        :rtype: BaseQuery
        """
        return ZenodoCommunity.get_irs(
            record, community_id=self.community.id, pid=pid)

    def has_record(self, record, pid=None, scope='any'):
        """Check if record is in a community.

        :type scope: str
        :param scope: Can take values 'any', 'all' or 'this'.
            * 'all': returns True if all record versions are in the community.
            * 'any': returns True if any of the record versions are in the
                community.
            * 'this': returns if the specified 'record' is in the community.
        """
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])

        pv = PIDVersioning(child=pid)
        if scope == 'this':
            return self.community.has_record(record)
        q = (self.community.has_record(
                ZenodoRecord.get_record(p.get_assigned_object()))
             for p in pv.children)
        if scope == 'all':
            return all(q)
        if scope == 'any':
            return any(q)

    def add_record(self, record, pid=None):
        """Add a record and all of its versions to a community."""
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])

        pv = PIDVersioning(child=pid)
        for child in pv.children.all():
            rec = ZenodoRecord.get_record(
                child.get_assigned_object())
            if not self.community.has_record(rec):
                self.community.add_record(rec)
                rec.commit()

    def accept_record(self, record, pid=None):
        """Accept the record and all of its versions into the community.

        :type record: zenodo.modules.records.api.ZenodoRecord
        :param pid: PID of type 'recid'
        :type pid: invenio_pidstore.models.PersistentIdentifier
        """
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])
        with db.session.begin_nested():
            pending_q = self.get_comm_irs(record, pid=pid)
            if not pending_q.count():
                raise InclusionRequestMissingError(community=self,
                                                   record=record)

            pv = PIDVersioning(child=pid)
            for child in pv.children.all():
                rec = ZenodoRecord.get_record(
                    child.get_assigned_object())
                self.community.add_record(rec)
                rec.commit()

                if request:
                    @after_this_request
                    def send_signals(response):
                        try:
                            record_accepted.send(
                                current_app._get_current_object(),
                                record_id=rec.id,
                                community_id=self.community.id,
                            )
                        except Exception:
                            pass
                        return response

            pending_q.delete(synchronize_session=False)

    def reject_record(self, record, pid=None):
        """Reject the inclusion request.

        :type record: zenodo.modules.records.api.ZenodoRecord
        """
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])
        with db.session.begin_nested():
            pending_q = self.get_comm_irs(record, pid=pid)
            pending_q.delete(synchronize_session=False)

    def remove_record(self, record, pid=None):
        """Remove the record and all of its versions from the community.

        :type record: zenodo.modules.records.api.ZenodoRecord
        """
        if not pid:
            pid = PersistentIdentifier.get('recid', record['recid'])

        with db.session.begin_nested():
            pv = PIDVersioning(child=pid)
            for child in pv.children.all():
                rec = ZenodoRecord.get_record(
                    child.get_assigned_object())
                if self.community.has_record(rec):
                    self.community.remove_record(rec)
                rec.commit()
