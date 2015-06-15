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

depends_on = [u'zenodo_2015_03_04_firerole_email_to_uid']


def info():
    """Information about the upgrade."""
    return "New subtypes addition: delivarable and milestone."


def do_upgrade():
    """Implement your upgrades here."""
    # deliverable addition
    run_sql(
        "INSERT INTO collection (name, dbquery) VALUES (%s, %s)",
        ('deliverable', '980__b:deliverable')
    )
    coll_id = run_sql(
        "SELECT id FROM collection WHERE name='deliverable'")[0][0]
    run_sql(
        "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs)\
        VALUES (%s, 'usage;comments;metadata;files')", (coll_id,)
    )
    run_sql(
        "INSERT INTO collection_collection (id_dad, id_son, type, score)\
        VALUES (%s, %s, %s, %s)", (2, coll_id, 'r', coll_id)
    )
    run_sql(
        "INSERT INTO collectionname (id_collection, ln, type, value)\
        VALUES (%s, %s, %s, %s)", (coll_id, 'en', 'ln', 'Project Deliverable')
    )

    # milestone addition
    run_sql(
        "INSERT INTO collection (name, dbquery) VALUES (%s, %s)",
        ('milestone', '980__b:milestone')
    )
    coll_id = run_sql(
        "SELECT id FROM collection WHERE name='milestone'")[0][0]
    run_sql(
        "INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs)\
        VALUES (%s, 'usage;comments;metadata;files')", (coll_id,)
    )
    run_sql(
        "INSERT INTO collection_collection (id_dad, id_son, type, score)\
        VALUES (%s, %s, %s, %s)", (2, coll_id, 'r', coll_id)
    )
    run_sql(
        "INSERT INTO collectionname (id_collection, ln, type, value)\
        VALUES (%s, %s, %s, %s)", (coll_id, 'en', 'ln', 'Project Milestone')
    )


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
