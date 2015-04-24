# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
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

"""Convenience module for importing utilities need in a shell."""

import os

from invenio.base.globals import cfg
from invenio.ext.cache import cache
from invenio.ext.login import UserInfo
from invenio.ext.sqlalchemy import db
from invenio.modules.accounts.models import User
from invenio.modules.deposit.models import Deposition, DepositionFile, \
    DepositionStorage, DepositionType
from invenio.modules.formatter import format_record
from invenio.modules.pidstore.models import PersistentIdentifier
from invenio.modules.pidstore.tasks import datacite_delete, \
    datacite_register, datacite_sync, datacite_update
from invenio.modules.records.api import get_record
from invenio.utils.serializers import ZlibPickle as Serializer
from werkzeug.utils import secure_filename


def ban_user(user_id):
    """Block user."""
    u = User.query.get(user_id)
    if u.note != '0':
        u.note = '0'
        db.session.commit()
    remove_session(user_id)


def remove_session(user_id):
    """Remove session for a user."""
    prefix = cache.cache.key_prefix + "session::"

    for k in cache.cache._client.keys():
        if k.startswith(prefix):
            k = k[len(cache.cache.key_prefix):]
            try:
                data = Serializer.loads(cache.get(k))
                if data['uid'] == user_id:
                    print k
                    cache.delete(k)
            except TypeError:
                pass


def deposition_users(depositions):
    """Iterate over deposition users."""
    for d in depositions:
        yield Deposition.get(d).user_id


def deposition_users_emails(depositions):
    """Get list of email addresses for depositions."""
    for user_id in deposition_users(depositions):
        yield User.query.get(user_id).email


def deposition_with_files(files, user_id=None, deposition_id=None):
    """Add very big files to a deposition."""
    if deposition_id:
        d = Deposition.get(deposition_id)
    else:
        d = Deposition.create(User.query.get(user_id))

    for filepath in files:
        with open(filepath, "rb") as fileobj:
            filename = os.path.basename(filepath)
            df = DepositionFile(backend=DepositionStorage(d.id))
            df.save(fileobj, filename=filename)
            d.add_file(df)
    return d
