# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Configuration for Zenodo Redirector."""

from __future__ import absolute_import, print_function

ZENODO_TYPE_SUBTYPE_LEGACY = {
    'publications': ('publications', None),
    'books': ('publications', 'books'),
    'books-sections': ('publications', 'sections'),
    'conference-papers': ('publications', 'conference-papers'),
    'journal-articles': ('publications', 'journal-articles'),
    'patents': ('publications', 'patents'),
    'preprints': ('publications', 'preprints'),
    'deliverable': ('publications', 'deliverable'),
    'milestone': ('publications', 'milestone'),
    'proposal': ('publications', 'proposal'),
    'reports': ('publications', 'reports'),
    'theses': ('publications', 'theses'),
    'technical-notes': ('publications', 'technical-notes'),
    'working-papers': ('publications', 'working-papers'),
    'other-publications': ('publications', 'other'),

    'posters': ('posters', None),

    'presentations': ('presentations', None),

    'datasets': ('datasets', None),

    'images': ('images', None),
    'figures': ('images', 'figures'),
    'drawings': ('images', 'drawings'),
    'diagrams': ('images', 'diagrams'),
    'photos': ('images', 'photos'),
    'other-images': ('images', 'other'),

    'videos': ('videos', None),

    'software': ('software', None),

    'lessons': ('lessons', None),
}
