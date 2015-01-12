# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from invenio.legacy.dbquery import run_sql

depends_on = [u'zenodo_2014_03_18_hstrecord_autoincrement']


def info():
    """Information about the upgrade."""
    return "Create Proposal subtype in Publications."


def do_upgrade():
    """Implement your upgrades here."""
    run_sql("INSERT INTO collection (name, dbquery)\
        VALUES (%s, %s)", ('proposal', '980__b:proposal'))
    coll_id = run_sql("SELECT id FROM collection WHERE name='proposal'")[0][0]
    run_sql("INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs)\
        VALUES (%s, 'usage;comments;metadata;files')", (coll_id,))
    run_sql("INSERT INTO collection_collection (id_dad, id_son, type, score)\
        VALUES (%s, %s, %s, %s)", (2, coll_id, 'r', coll_id),)
    run_sql("INSERT INTO collectionname (id_collection, ln, type, value)\
        VALUES (%s, %s, %s, %s)", (coll_id, 'en', 'ln', 'Proposal'),)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
