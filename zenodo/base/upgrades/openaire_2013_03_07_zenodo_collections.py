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


depends_on = ['openaire_2013_03_07_zenodo_migration']


collections = [
    (1, 'ZENODO', '980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (2, 'publications', '980__a:publication'),
    (3, 'posters', '980__a:poster'),
    (4, 'presentations', '980__a:presenation'),
    (5, 'datasets', '980__a:dataset'),
    (6, 'images', '980__a:image'),
    (7, 'videos', '980__a:video'),

    (8, 'books', '980__b:book'),
    (9, 'book-sections', '980__bsection'),
    (10, 'conference-papers', '980__b:conferencepaper'),
    (11, 'journal-articles', '980__b:article'),
    (12, 'patents', '980__b:patent'),
    (13, 'preprints', '980__b:preprint'),
    (14, 'reports', '980__b:report'),
    (15, 'theses', '980__b:thesis'),
    (16, 'technical-notes', '980__b:technicalnote'),
    (17, 'working-papers', '980__b:workingpaper'),
    (18, 'other-publications', '980__a:publication AND 980__b:other'),

    (20, 'figures', '980__b:figure'),
    (21, 'plots', '980__b:plot'),
    (22, 'drawings', '980__b:drawing'),
    (23, 'diagrams', '980__b:diagram'),
    (24, 'photos', '980__b:photo'),
    (25, 'other-images', '980__a:image AND 980__b:other'),

    (26, 'open', '(542__l:open OR 542__l:embargoed) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (27, 'closed', '(542__l:closed OR 542__l:restricted) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),

    (28, 'hidden', '980__a:PROVISIONAL OR 980__a:PENDING OR 980__a:SPAM OR 980__a:REJECTED OR 980__a:DARK'),


    (29, 'communities', '980__a:user-*'),

    (30, 'provisional', '980__a:0->Z AND NOT 980__a:curated AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
]

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
    return "Setup ZENODO collections"


def do_upgrade():
    """ Implement your upgrades here  """
    # Wipe old collections
    run_sql("DELETE FROM collection")
    run_sql("DELETE FROM collectiondetailedrecordpagetabs")
    run_sql("DELETE FROM collection_collection")
    run_sql("DELETE FROM collectionname")

    run_sql("DELETE FROM accROLE_accACTION_accARGUMENT WHERE id_accROLE=12 OR id_accROLE=1 OR id_accROLE=3 OR id_accROLE=11")  # admin, any, auth, curator
    run_sql("DELETE FROM accROLE_accACTION_accARGUMENT WHERE id_accACTION=34 or id_accACTION=29")  # viewrestcoll/submit actions
    run_sql("DELETE FROM accARGUMENT")
    run_sql("UPDATE accROLE SET name='curators' WHERE id=12")

    for coll in collections:
        run_sql("INSERT INTO collection (id, name, dbquery) VALUES (%s, %s, %s)", coll)
        run_sql("INSERT INTO collectiondetailedrecordpagetabs (id_collection, tabs) VALUES (%s, 'usage;comments;metadata;files')", (coll[0],))

    for r in relations:
        run_sql("INSERT INTO collection_collection (id_dad, id_son, type, score) VALUES (%s, %s, %s, %s)", r)

    for arg in accargs:
        run_sql("INSERT INTO accARGUMENT (id, keyword, value) VALUES (%s, %s, %s)", arg)

    for r in restrictions:
        run_sql("INSERT INTO accROLE_accACTION_accARGUMENT (id_accROLE, id_accACTION, id_accARGUMENT, argumentlistid) VALUES (%s, %s, %s, %s)", r)

    for n in names:
        run_sql("INSERT INTO collectionname (id_collection, ln, type, value) VALUES (%s, %s, %s, %s)", n)

    for f in formats:
        run_sql("INSERT INTO collection_format (id_collection, id_format, score) VALUES (%s, %s, %s)", f)


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 1
