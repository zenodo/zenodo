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

data = [
    (1, 'HTML brief', 'hb', 'HTML brief output format, used for search results pages.', 'text/html', 1),
    (2, 'HTML detailed', 'hd', 'HTML detailed output format, used for Detailed record pages.', 'text/html', 1),
    (3, 'MARC', 'hm', 'HTML MARC.', 'text/html', 1),
    (4, 'Dublin Core', 'xd', 'XML Dublin Core.', 'text/xml', 1),
    (5, 'MARCXML', 'xm', 'XML MARC.', 'text/xml', 1),
    (6, 'portfolio', 'hp', 'HTML portfolio-style output format for photos.', 'text/html', 1),
    (7, 'photo captions only', 'hc', 'HTML caption-only output format for photos.', 'text/html', 1),
    (8, 'BibTeX', 'hx', 'BibTeX.', 'text/html', 1),
    (9, 'EndNote', 'xe', 'XML EndNote.', 'text/xml', 1),
    (10, 'NLM', 'xn', 'XML NLM.', 'text/xml', 1),
    (11, 'Excel', 'excel', 'Excel csv output', 'application/ms-excel', 0),
    (12, 'HTML similarity', 'hs', 'Very short HTML output for similarity box (<i>people also viewed..</i>).', 'text/html', 0),
    (13, 'RSS', 'xr', 'RSS.', 'text/xml', 0),
    (14, 'OAI DC', 'xoaidc', 'OAI DC.', 'text/xml', 0),
    (15, 'File mini-panel', 'hdfile', 'Used to show fulltext files in mini-panel of detailed record pages.', 'text/html', 0),
    (16, 'Actions mini-panel', 'hdact', 'Used to display actions in mini-panel of detailed record pages.', 'text/html', 0),
    (17, 'References tab', 'hdref', 'Display record references in References tab.', 'text/html', 0),
    (18, 'HTML citesummary', 'hcs', 'HTML cite summary format, used for search results pages.', 'text/html', 1),
    (19, 'RefWorks', 'xw', 'RefWorks.', 'text/xml', 1),
    (20, 'MODS', 'xo', 'Metadata Object Description Schema', 'application/xml', 1),
    (23, 'Podcast', 'xp', 'Sample format suitable for multimedia feeds, such as podcasts', 'application/rss+xml', 0),
    (22, 'OAI DC OpenAIRE', 'untld2', '', 'text/xml', 0),
    (24, 'DataCite', 'dcite', 'DataCite XML Metadata Kernel', 'text/xml', 1),
    (25, 'HTML brief provisional', 'hbpro', 'HTML brief provisional output format.', 'text/html', 0),
    (26, 'HTML detailed curation', 'hdcur', 'HTML detailed curation output format.', 'text/html', 0),
    (27, 'OAI DataCite', 'oaidci', 'OAI Datacite Metadata Schema', 'text/xml', 0),
    (28, 'DataCite 3.0', 'dcite3', 'DataCite XML Metadata Kernel 3.0', 'text/xml', 0),
    (29, 'OAI DataCite 3.0', 'oaidc3', 'OAI DataCite XML Metadata Kernel 3.0', 'text/xml', 0),
    (30, 'WebAuthorProfile data helper', 'wapdat', 'cPickled dicts', 'text', 0),
]


class FormatData(DataSet):
    pass

for i, n, c, d, t, v in data:
    class obj:
        id = i
        name = n
        code = c
        description = d
        content_type = t
        visibility = v
    obj.__name__ = "f%s" % i
    setattr(FormatData, obj.__name__, obj)
