# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2014, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
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

from fixture import DataSet

from invenio.modules.search import fixtures


# ===========
# Collections
# ===========
class CollectionData(DataSet):
    pass

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
    (19, 'Figures', 'figures', '980__b:figure'),
    (20, 'Plots', 'plots', '980__b:plot'),
    (21, 'Drawings', 'drawings', '980__b:drawing'),
    (22, 'Diagrams', 'diagrams', '980__b:diagram'),
    (23, 'Photos', 'photos', '980__b:photo'),
    (24, 'Other', 'other-images', '980__a:image AND 980__b:other'),
    (25, 'Open access', 'open', '(542__l:open OR 542__l:embargoed) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (26, 'Closed access', 'closed', '(542__l:closed OR 542__l:restricted) AND 980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (27, 'Hidden', 'hidden', '980__a:PROVISIONAL OR 980__a:PENDING OR 980__a:SPAM OR 980__a:REJECTED OR 980__a:DARK'),
    (28, 'Communities', 'communities', '980__a:user-*'),
    # zenodo-public is a restricted collection with access from anyuser. This
    # is to ensure that even though a record belongs to a provisional
    # collection it can still be viewed by guest users.
    (29, 'zenodo-public', 'zenodo-public', '980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DARK'),
    (30, 'Software', 'software', '980__a:software'),
    (31, 'Proposal', 'proposal', '980__b:proposal'),
    (32, 'Project Deliverables', 'deliverables', '980__b:deliverable'),
    (33, 'Project Milestones', 'milestones', '980__b:milestone'),
    (34, 'Lessons', 'lessons', '980__a:lesson'),

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
    (1, 30, 'r', 6),
    (1, 34, 'r', 7),
    (1, 7, 'r', 8),
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
    (1, 25, 'v', 25),
    (1, 26, 'v', 26),
    (1, 28, 'v', 27),
    (2, 31, 'r', 28),
    (2, 32, 'r', 29),
    (2, 33, 'r', 30),
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


class Field_18:
    code = u'doi'
    id = 18
    name = u'doi'
fixtures.FieldData.Field_18 = Field_18


class Field_45:
    code = u'access_rights'
    id = 45
    name = u'access rights'
fixtures.FieldData.Field_45 = Field_45


class Field_46:
    code = u'EU Project'
    id = 46
    name = u'project'
fixtures.FieldData.Field_46 = Field_46


class Tag_227:
    id = 227
    value = u'0247_a'
    recjson_value = u'doi'
    name = u'doi'
fixtures.TagData.Tag_227 = Tag_227


class Tag_228:
    id = 228
    value = u'542__l'
    recjson_value = u'access_right'
    name = u'access rights'
fixtures.TagData.Tag_228 = Tag_228


class Tag_229:
    id = 229
    value = u'536__c'
    recjson_value = u'grants[n].identifier'
    name = u'EU Project grant agreement number'
fixtures.TagData.Tag_229 = Tag_229


class Tag_230:
    id = 230
    value = u'536__a'
    recjson_value = u'grants[n].description'
    name = u'EU Project description'
fixtures.TagData.Tag_230 = Tag_230


class FieldTag_227_18:
    score = 100
    id_tag = fixtures.TagData.Tag_227.id
    id_field = fixtures.FieldData.Field_18.id
fixtures.FieldTagData.FieldTag_227_18 = FieldTag_227_18


class FieldTag_228_45:
    score = 100
    id_tag = fixtures.TagData.Tag_228.id
    id_field = fixtures.FieldData.Field_45.id
fixtures.FieldTagData.FieldTag_228_45 = FieldTag_228_45


class FieldTag_229_46:
    score = 100
    id_tag = fixtures.TagData.Tag_229.id
    id_field = fixtures.FieldData.Field_46.id
fixtures.FieldTagData.FieldTag_229_46 = FieldTag_229_46


class FieldTag_230_46:
    score = 100
    id_tag = fixtures.TagData.Tag_230.id
    id_field = fixtures.FieldData.Field_46.id
fixtures.FieldTagData.FieldTag_229_46 = FieldTag_230_46
