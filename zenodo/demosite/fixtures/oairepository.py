# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
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

from __future__ import absolute_import

from fixture import DataSet


class OaiREPOSITORYData(DataSet):
    class oa:
        id = 22
        setName = "OpenAIRE"
        setSpec = "openaire"
        setCollection = "publications, posters, presentations, images, videos"
        setDescription = ""
        setDefinition = "c=publications, posters, presentations, images, videos;p1=open;f1=access_rights;m1=e;op1=o;p2=user-ecfunded;f2=collection;m2=e;op2=n;p3=hidden;f3=collection;m3=e;"
        p1 = "open"
        f1 = "access_rights"
        m1 = "e"
        p2 = "user-ecfunded"
        f2 = "collection"
        m2 = "e"
        p3 = "hidden"
        f3 = "collection"
        m3 = "e"

    class oa_plus:
        id = 23
        setName = "OpenAIRE Datasets"
        setSpec = "openaire_data"
        setCollection = "datasets"
        setDescription = ""
        setDefinition = "c=datasets;p1=datasets;f1=collection;m1=e;op1=n;p2=hidden;f2=collection;m2=e;op2=a;p3=;f3=;m3=;"
        p1 = "datasets"
        f1 = "collection"
        m1 = "e"
        p2 = "hidden"
        f2 = "collection"
        m2 = "e"
        p3 = ""
        f3 = ""
        m3 = ""
