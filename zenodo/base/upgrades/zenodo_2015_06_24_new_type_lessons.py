# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2015 CERN.
#
# ZENODO is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio.legacy.dbquery import run_sql

depends_on = [u'zenodo_2015_06_10_fix_alternate_identifiers']


def info():
    """Information about the upgrade."""
    return "New type addition: lessons."


def do_upgrade():
    """Implement your upgrades here."""
    run_sql(
        "INSERT INTO collection (name, dbquery) VALUES (%s, %s)",
        ('lessons', '980__a:lessons')
    )
    parent_id = 1
    pos = 13
    coll_id = run_sql(
        "SELECT id FROM collection WHERE name='lessons'")[0][0]
    run_sql(
        "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs)\
        VALUES (%s, 'usage;comments;metadata;files')", (coll_id,)
    )
    run_sql(
        "UPDATE collection_collection SET score=score+1 "
        "WHERE id_dad=%s AND score>=%s",
        (parent_id, pos)
    )
    run_sql(
        "INSERT INTO collection_collection (id_dad, id_son, type, score)\
        VALUES (%s, %s, %s, %s)", (parent_id, coll_id, 'r', pos)
    )
    run_sql(
        "INSERT INTO collectionname (id_collection, ln, type, value)\
        VALUES (%s, %s, %s, %s)", (coll_id, 'en', 'ln', 'Lessons')
    )


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
