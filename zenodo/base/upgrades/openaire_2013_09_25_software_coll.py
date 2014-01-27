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

import warnings
from invenio.legacy.dbquery import run_sql
from invenio.utils.text import wait_for_user


depends_on = ['openaire_2013_06_25_expjob_rename']

relations = [
    (1, 2, 'r', 1),
    (1, 3, 'r', 2),
    (1, 4, 'r', 3),
    (1, 5, 'r', 4),
    (1, 6, 'r', 5),
    (1, 7, 'r', 6),

    (2, 8, 'r', 7),
    (2, 9, 'r', 8),
    (2, 10, 'r', 9),
    (2, 11, 'r', 10),
    (2, 12, 'r', 11),
    (2, 13, 'r', 12),
    (2, 14, 'r', 13),
    (2, 15, 'r', 14),
    (2, 16, 'r', 15),
    (2, 17, 'r', 16),
    (2, 18, 'r', 17),

    (6, 20, 'r', 18),
    (6, 21, 'r', 19),
    (6, 22, 'r', 20),
    (6, 23, 'r', 21),
    (6, 24, 'r', 22),
    (6, 25, 'r', 23),

    (1, 26, 'v', 24),
    (1, 27, 'v', 25),
]

accargs = (
    (10, 'collection', 'hidden'),
    (11, 'categ', '*'),
    (12, 'doctype', 'ZENODO'),
    (13, 'act', '*'),
    (14, 'collection', 'provisional'),
)


restrictions = [
    # viewrestcoll
    (1, 34, 10, 1),  # admin
    #(12, 34, 10, 1),  # curator
    (1, 34, 14, 1),  # admin
    (12, 34, 14, 1),  # curator

    # submit
    (1, 29, 11, 1),  # admin
    (1, 29, 12, 1),  # admin
    (1, 29, 13, 1),  # admin

    (12, 29, 11, 1),  # curator
    (12, 29, 12, 1),  # curator
    (12, 29, 13, 1),  # curator

    (11, 29, 11, 1),  # auth user
    (11, 29, 12, 1),  # auth user
    (11, 29, 13, 1),  # auth user
]

names = [
    (1, 'en', 'ln', 'ZENODO'),
    (2, 'en', 'ln', 'Publications'),
    (3, 'en', 'ln', 'Posters'),
    (4, 'en', 'ln', 'Presentations'),
    (5, 'en', 'ln', 'Datasets'),
    (6, 'en', 'ln', 'Images'),
    (7, 'en', 'ln', 'Videos/Audio'),
    (8, 'en', 'ln', 'Books'),
    (9, 'en', 'ln', 'Book sections'),
    (10, 'en', 'ln', 'Conference papers'),
    (11, 'en', 'ln', 'Journal articles'),
    (12, 'en', 'ln', 'Patents'),
    (13, 'en', 'ln', 'Preprints'),
    (14, 'en', 'ln', 'Reports'),
    (15, 'en', 'ln', 'Theses'),
    (16, 'en', 'ln', 'Technical notes'),
    (17, 'en', 'ln', 'Working papers'),
    (18, 'en', 'ln', 'Other'),
    (20, 'en', 'ln', 'Figures'),
    (21, 'en', 'ln', 'Plots'),
    (22, 'en', 'ln', 'Drawings',),
    (23, 'en', 'ln', 'Diagrams'),
    (24, 'en', 'ln', 'Photos'),
    (25, 'en', 'ln', 'Other'),
    (26, 'en', 'ln', 'Open Access'),
    (27, 'en', 'ln', 'Closed Access'),
    (28, 'en', 'ln', 'Hidden'),
    (29, 'en', 'ln', 'Communities'),
    (30, 'en', 'ln', 'Provisional'),
]


formats = [
    (30, 26, 1),
]


def info():
    return "Create software collection"


def do_upgrade():
    """ Implement your upgrades here  """
    run_sql("INSERT INTO collection (name, dbquery) VALUES (%s, %s)", ('software', '980__a:software'))
    coll_id = run_sql("SELECT id FROM collection WHERE name='software'")[0][0]
    run_sql("INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (%s, 'usage;comments;metadata;files')", (coll_id,))
    run_sql("INSERT INTO collection_collection (id_dad, id_son, type, score) VALUES (%s, %s, %s, %s)", (1, coll_id, 'r', 6),)
    run_sql("INSERT INTO collectionname (id_collection, ln, type, value) VALUES (%s, %s, %s, %s)", (coll_id, 'en', 'ln', 'Software'),)


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 1
