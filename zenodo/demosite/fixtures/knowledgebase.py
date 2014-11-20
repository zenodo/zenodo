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

from __future__ import absolute_import
from fixture import DataSet
import csv
from os.path import dirname, join


class KnwKBData(DataSet):
    class json_projects:
        id = 1
        name = "json_projects"
        description = ""
        type = "w"

    class licenses:
        id = 2
        name = "licenses"
        description = ""
        type = "w"


class KnwKBRVALData(DataSet):
    pass
    """ Install license data into knowledge base """


data = (
    ('kb_licenses.csv', KnwKBData.licenses.id),
    ('kb_json_projects.csv', KnwKBData.json_projects.id),
)

idx = 0
for filename, kb_id in data:
    with open(join(dirname(__file__), filename), 'r') as f:
        reader = csv.reader(
            f, delimiter=',', quotechar='"', doublequote=False, escapechar='\\'
        )
        for row in reader:
            class obj:
                m_key = row[1]
                m_value = row[2]
                id_knwKB = kb_id
            obj.__name__ = "kbval{0}".format(idx)
            setattr(KnwKBRVALData, obj.__name__, obj)
            idx += 1
