# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import warnings
from invenio.dbquery import run_sql
from invenio.inveniocfg_upgrader import run_sql_ignore


depends_on = ['openaire_initial']


def info():
    return "Zenodo data migration"


def do_upgrade():
    from invenio import config

    # Portalboxes upgrade
    run_sql_ignore("""DELETE FROM collection_portalbox WHERE id_portalbox=1 or id_portalbox=2;""")
    run_sql_ignore("""DELETE FROM portalbox WHERE id=1 or id=2;""")

    # Main collection name
    run_sql_ignore("UPDATE collection SET name=%s WHERE id=1", (config.CFG_SITE_NAME,))

    # Available tabs
    run_sql_ignore("""DELETE FROM collectiondetailedrecordpagetabs;""")
    for r in run_sql("""SELECT id FROM collection"""):
        run_sql("""INSERT INTO collectiondetailedrecordpagetabs VALUES (%s,'usage;comments;metadata;files')""", r)


def estimate():
    return 1
