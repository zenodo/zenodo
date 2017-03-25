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
    'publications': ('publication', None),
    'books': ('publication', 'book'),
    'books-sections': ('publication', 'section'),
    'conference-papers': ('publication', 'conferencepaper'),
    'journal-articles': ('publication', 'article'),
    'patents': ('publication', 'patent'),
    'preprints': ('publication', 'preprint'),
    'deliverable': ('publication', 'deliverable'),
    'milestone': ('publication', 'milestone'),
    'proposal': ('publication', 'proposal'),
    'reports': ('publication', 'report'),
    'theses': ('publication', 'thesis'),
    'technical-notes': ('publication', 'technicalnote'),
    'working-papers': ('publication', 'workingpaper'),
    'other-publications': ('publication', 'other'),

    'posters': ('poster', None),

    'presentations': ('presentation', None),

    'datasets': ('dataset', None),

    'images': ('image', None),
    'figures': ('image', 'figure'),
    'drawings': ('image', 'drawing'),
    'diagrams': ('image', 'diagram'),
    'photos': ('image', 'photo'),
    'other-images': ('image', 'other'),

    'videos': ('video', None),

    'software': ('software', None),

    'lessons': ('lesson', None),
}


#: External redirect URLs
REDIRECTOR_EXTERNAL_REDIRECTS = [
    ['/dev', 'dev', 'http://developers.zenodo.org'],
    ['/faq', 'faq', 'http://help.zenodo.org'],
    ['/features', 'features', 'http://help.zenodo.org/features/'],
    ['/whatsnew', 'whatsnew', 'http://help.zenodo.org/whatsnew/'],
    ['/about', 'about', 'http://about.zenodo.org'],
    ['/contact', 'contact', 'http://about.zenodo.org/contact/'],
    ['/policies', 'policies', 'http://about.zenodo.org/policies/'],
    ['/privacy-policy', 'privacy-policy',
     'http://about.zenodo.org/privacy-policy/'],
    ['/terms', 'terms', 'http://about.zenodo.org/terms/'],
    ['/donate', 'donate', 'https://giving.web.cern.ch/civicrm/contribute/'
                          'transact%3Freset%3D1%26id%3D20'],
]
