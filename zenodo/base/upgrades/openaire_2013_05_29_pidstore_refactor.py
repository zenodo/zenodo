# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from sqlalchemy import *
from invenio.ext.sqlalchemy import db

depends_on = ['openaire_2013_05_02_pidstore']


def info():
    return "Create pid, pidLOG, pidREGISTRY"


def do_upgrade():
    """ Implement your upgrades here  """
    conn = db.engine.connect()

    # Alter tables
    conn.execute("ALTER TABLE pid ADD COLUMN object_type varchar(3) AFTER pid")
    conn.execute("ALTER TABLE pid ADD COLUMN object_id varchar(255) AFTER object_type")
    conn.execute("ALTER TABLE pid ADD INDEX idx_object_type_id (object_type, object_id)")

    # Migrate content
    m = db.MetaData(bind=db.engine)
    m.reflect()

    t = m.tables['pid']
    r = m.tables['pidREGISTRY']

    for otype, oid, pid in db.session.query(r).all():
        stmt = t.update().where(t.c.id == pid).values(object_type=otype, object_id=oid)
        conn.execute(stmt)

    # Drop old table
    r.drop()
