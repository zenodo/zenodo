# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
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

from invenio.config import CFG_SITE_NAME
from fixture import DataSet


# ===========
# Collections
# ===========
class CollectionData(DataSet):
    class zenodo:
        id = 1
        name = CFG_SITE_NAME
        dbquery = '980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'


colls = [
    (2, 'Publications', 'publications', '980__a:publication'),
    (3, 'Posters', 'posters', '980__a:poster'),
    (4, 'Presentations', 'presentations', '980__a:presentation'),
    (5, 'Datasets', 'datasets', '980__a:dataset'),
    (6, 'Images', 'images', '980__a:image'),
    (7, 'Videos', 'videos', '980__a:video'),
    (8, 'Books', 'books', '980__b:book'),
    (9, 'Book sections', 'book-sections', '980__b:section'),
    (10, 'Conference papers', 'conference-papers', '980__b:conferencepaper'),
    (11, 'Journal articles', 'journal-articles', '980__b:article'),
    (12, 'Patents', 'patents', '980__b:patent'),
    (13, 'Preprints', 'preprints', '980__b:preprint'),
    (14, 'Reports', 'reports', '980__b:report'),
    (15, 'Theses', 'theses', '980__b:thesis'),
    (16, 'Technical notes', 'technical-notes', '980__b:technicalnote'),
    (17, 'Working papers', 'working-papers', '980__b:workingpaper'),
    (18, 'Other', 'other-publications', '980__a:publication AND 980__b:other'),
    (20, 'Figures', 'figures', '980__b:figure'),
    (21, 'Plots', 'plots', '980__b:plot'),
    (22, 'Drawings', 'drawings', '980__b:drawing'),
    (23, 'Diagrams', 'diagrams', '980__b:diagram'),
    (24, 'Photos', 'photos', '980__b:photo'),
    (25, 'Other', 'other-images', '980__a:image AND 980__b:other'),
    (26, 'Open access', 'open', '(542__l:open OR 542__l:embargoed) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (27, 'Closed access', 'closed', '(542__l:closed OR 542__l:restricted) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (28, 'Hidden', 'hidden', '980__a:PROVISIONAL OR 980__a:PENDING OR 980__a:SPAM OR 980__a:REJECTED OR 980__a:DARK'),
    (29, 'Communities', 'communities', '980__a:user-*'),
    (153, 'Software', 'software', '980__a:software'),
]

idx = 2
for i, t, n, q in colls:
    class obj(object):
        id = idx
        name = n
        dbquery = q
        names = {
            ('en', 'ln'): t,
        }
    obj.__name__ = n
    idx += 1
    setattr(CollectionData, n, obj)


# ===============
# Collection Tree
# ===============
coll_coll_data = (
    (1, 2, 'r', 1),
    (1, 3, 'r', 2),
    (1, 4, 'r', 3),
    (1, 5, 'r', 4),
    (1, 6, 'r', 5),
    (1, 29, 'r', 6),
    (1, 7, 'r', 7),
    (2, 8, 'r', 8),
    (2, 9, 'r', 9),
    (2, 10, 'r', 10),
    (2, 11, 'r', 11),
    (2, 12, 'r', 12),
    (2, 13, 'r', 13),
    (2, 14, 'r', 14),
    (2, 15, 'r', 15),
    (2, 16, 'r', 16),
    (2, 17, 'r', 17),
    (2, 18, 'r', 18),
    (6, 19, 'r', 19),
    (6, 20, 'r', 20),
    (6, 21, 'r', 21),
    (6, 22, 'r', 22),
    (6, 23, 'r', 23),
    (6, 24, 'r', 24),

)


class CollectionCollectionData(DataSet):
    pass


idx = 1
for d, s, t, scr in coll_coll_data:
    class obj(object):
        id_dad = d
        id_son = s
        score = scr
        type = t
    obj.__name__ = "cc%s" % idx
    idx += 1
    setattr(CollectionCollectionData, obj.__name__, obj)


# ===============
# Collection tabs
# ===============
class CollectiondetailedrecordpagetabsData(DataSet):
    pass

coll_ids = [1] + [x[0] for x in colls]

for cid in coll_ids:
    class obj(object):
        id_collection = cid
        tabs = 'usage;comments;metadata;files'
    obj.__name__ = "ctabs%s" % cid
    setattr(CollectiondetailedrecordpagetabsData, obj.__name__, obj)
