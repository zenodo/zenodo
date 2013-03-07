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
from invenio.textutils import wait_for_user


depends_on = ['openaire_2013_03_07_zenodo_migration']


collections = [
    (1, 'ZENODO', 'collection:0->Z AND NOT collection:PROVISIONAL AND NOT collection:PENDING AND NOT collection:SPAM AND NOT collection:REJECTED AND NOT collection:DARK'),
    (2, 'Publications', 'collection:publication'),
    (3, 'Posters', 'collection:poster'),
    (4, 'Presentations', 'collection:presenation'),
    (5, 'Datasets', 'collection:dataset'),
    (6, 'Images', 'collection:image'),
    (7, 'Videos/Audio', 'collection:video'),

    (8, 'Books', '980__b:book'),
    (9, 'Book sections', '980__bsection'),
    (10, 'Conference papers', '980__b:conferencepaper'),
    (11, 'Journal articles', '980__b:article'),
    (12, 'Patents', '980__b:patent'),
    (13, 'Preprints', '980__b:preprint'),
    (14, 'Reports', '980__b:report'),
    (15, 'Theses', '980__b:thesis'),
    (16, 'Technical notes', '980__b:technicalnote'),
    (17, 'Working papers', '980__b:workingpaper'),
    (18, 'Other publications', '980__b:other'),

    (20, 'Figures', '980__b:figure'),
    (21, 'Plots', '980__b:plot'),
    (22, 'Drawings', '980__b:drawing'),
    (23, 'Diagrams', '980__b:diagram'),
    (24, 'Photos', '980__b:photo'),
    (25, 'Other images', '980__b:other'),

    (26, 'Open Access', '(542__l:open OR 542__l:embargoed) AND collection:0->Z AND NOT collection:PROVISIONAL AND NOT collection:PENDING AND NOT collection:SPAM AND NOT collection:REJECTED AND NOT collection:DARK'),
    (27, 'Closed Access', '(542__l:closed OR 542__l:restricted) AND collection:0->Z AND NOT collection:PROVISIONAL AND NOT collection:PENDING AND NOT collection:SPAM AND NOT collection:REJECTED AND NOT collection:DARK'),

    (28, 'Hidden', 'collection:PROVISIONAL OR collection:PENDING OR collection:SPAM OR collection:REJECTED OR collection:DARK'),

    (29, 'Curated', 'collection:curated AND NOT collection:PROVISIONAL AND NOT collection:PENDING AND NOT collection:SPAM AND NOT collection:REJECTED AND NOT collection:DARK'),
    (30, 'Uncurated', 'collection:0->Z AND NOT collection:curated AND NOT collection:PROVISIONAL AND NOT collection:PENDING AND NOT collection:SPAM AND NOT collection:REJECTED AND NOT collection:DARK'),
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

    (1, 29, 'v', 26),
    (1, 30, 'v', 27),
]

accargs = (
    (10, 'collection', 'Hidden'),
    (11, 'categ', '*'),
    (12, 'doctype', 'ZENODO'),
    (13, 'act', '*'),
)


restrictions = [
    # viewrestcoll
    (1, 34, 10, 1),  # admin
    (12, 34, 10, 1),  # curator

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
    (29, 'en', 'ln', 'Curated'),
    (30, 'en', 'ln', 'Uncurated'),
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



def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 1
