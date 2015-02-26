# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


import warnings
from sqlalchemy import *
from invenio.ext.sqlalchemy import db


depends_on = [u'zenodo_2014_11_25_workflowobjectfix']


def info():
    return "Import ORCIDs into userEXT table."


def do_upgrade():
    # TODO:
    # - Test what happens when an orcid is unlinked from one account and then
    #   linked to another account afterwards.
    # - Test what happens if ORCID is already linked to another account.
    from invenio.modules.oauthclient.models import RemoteAccount
    from invenio.modules.accounts.models import UserEXT

    data = {}
    for a in RemoteAccount.query.filter_by(client_id='0000-0001-8135-3489'):
        orcid = a.extra_data.get('orcid', None)
        if orcid is not None:
            if orcid not in data:
                data[orcid] = []
            data[orcid].append(a.user_id)

    for orcid, users in data.items():
        if len(users) == 1:
            id_user = users[0]
            orcid_obj = UserEXT.query.filter_by(id=orcid, method='orcid').one()
            user_obj = UserEXT.query.filter_by(id_user=id_user,
                                               method='orcid').one()

            if not (orcid_obj or user_obj):
                ue = UserEXT(id=orcid, method='orcid', id_user=id_user)
                db.session.add(ue)
                db.session.commit()
            else:
                warnings.warn("ORCID %s or user %s already assigned." %
                              (orcid, id_user))
        else:
            warnings.warn("ORCID %s has multiple users %s" % (orcid, users))


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 5
