# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Configuration for Zenodo Records."""

from __future__ import absolute_import, print_function

from flask_babelex import gettext
from speaklater import make_lazy_gettext

_ = make_lazy_gettext(lambda: gettext)

ZENODO_RELATION_RULES = {
    'f1000research': [{
        'prefix': '10.12688/f1000research',
        'relation': 'isCitedBy',
        'scheme': 'doi',
        'text': 'Published in',
        'image': 'img/f1000research.jpg',
        }],
    'inspire': [{
        'prefix': 'http://inspirehep.net/record/',
        'relation': 'isSupplementedBy',
        'scheme': 'url',
        'text': 'Available in',
        'image': 'img/inspirehep.png',
        }],
    'briefideas': [{
        'prefix': 'http://beta.briefideas.org/',
        'relation': 'isIdenticalTo',
        'scheme': 'url',
        'text': 'Published in',
        'image': 'img/briefideas.png',
        }],
    'zenodo': [{
        'prefix': 'https://github.com',
        'relation': 'isSupplementTo',
        'scheme': 'url',
        'text': 'Available in',
        'image': 'img/github.png',
        }, {
        'prefix': '10.1109/JBHI',
        'relation': 'isCitedBy',
        'scheme': 'doi',
        'text': 'Published in',
        'image': 'img/ieee.jpg',
        }],
}

ZENODO_RELATION_TYPES = [
    ('isCitedBy', _('Cited by')),
    ('cites', _('Cites')),
    ('isSupplementTo', _('Supplement to')),
    ('isSupplementedBy', _('Supplementary material')),
    ('references', _('References')),
    ('isReferencedBy', _('Referenced by')),
    ('isNewVersionOf', _('Previous versions')),
    ('isPreviousVersionOf', _('New versions'))
]

ZENODO_LOCAL_DOI_PREFIXES = []
