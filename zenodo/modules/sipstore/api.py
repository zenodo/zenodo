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

"""Zenodo SIPStore API."""

from __future__ import absolute_import

import json

from flask import has_request_context, request
from flask_login import current_user
from invenio_db import db
from invenio_sipstore.models import SIP, RecordSIP, SIPFile


class ZenodoSIP(object):
    """API for creating Zenodo-specific SIPs."""

    @staticmethod
    def _build_agent_info():
        """Build the SIP agent info.

        :returns: Agent information regarding the SIP.
        :rtype: dict
        """
        agent = dict()
        if has_request_context() and request.remote_addr:
            agent['ip_address'] = request.remote_addr
            if current_user.is_authenticated and current_user.email:
                agent['email'] = current_user.email
        return agent

    @classmethod
    def create(cls, pid, record, create_sip_files=True, user_id=None,
               agent=None):
        """Create a Zenodo SIP, from the PID and the Record.

        Apart from the SIP itself, it also creates ``RecordSIP`` for the
        SIP-PID-Record relationship, as well as ``SIPFile`` objects for each
        the files in the record.
        Those objects are not returned by this function but can be fetched by
        the corresponding SIP relationships 'record_sips' and 'sip_files'.
        :param pid: PID of the published record ('recid').
        :type pid: `invenio_pidstore.models.PersistentIdentifier`
        :param record: Record for which the SIP should be created.
        :type record: `invenio_records.api.Record`
        :param create_sip_files: If True the SIPFiles will be created.
        :type create_sip_files: bool
        :returns: A Zenodo-specifi SIP object.
        :rtype: ``invenio_sipstore.models.SIP``
        """
        if not user_id:
            user_id = (None if current_user.is_anonymous
                       else current_user.get_id())
        if not agent:
            agent = cls._build_agent_info()

        with db.session.begin_nested():
            sip = SIP.create('json', json.dumps(record.dumps()),
                             user_id=user_id, agent=agent)
            recsip = RecordSIP(sip_id=sip.id, pid_id=pid.id)
            db.session.add(recsip)
            if record.files and create_sip_files:
                for f in record.files:
                    sf = SIPFile(sip_id=sip.id, filepath=f.key,
                                 file_id=f.file_id)
                    db.session.add(sf)
        return sip
