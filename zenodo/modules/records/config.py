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

import six
from flask_babelex import gettext
from speaklater import make_lazy_gettext

_ = make_lazy_gettext(lambda: gettext)

ZENODO_RECORDS_UI_CITATIONS_ENDPOINT = 'https://zenodo-broker-qa.web.cern.ch/api/relationships'

ZENODO_RECORDS_UI_CITATIONS_ENABLE = False

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

ZENODO_COMMUNITY_BRANDING = [
    'biosyslit',
    'lory',
]

ZENODO_RELATION_TYPES = [
    ('isCitedBy', _('Cited by')),
    ('cites', _('Cites')),
    ('isSupplementTo', _('Supplement to')),
    ('isSupplementedBy', _('Supplementary material')),
    ('references', _('References')),
    ('isReferencedBy', _('Referenced by')),
    ('isPublishedIn', _('Published in')),
    ('isNewVersionOf', _('Previous versions')),
    ('isPreviousVersionOf', _('New versions')),
    ('isContinuedBy', _('Continued by')),
    ('continues', _('Continues')),
    ('IsDescribedBy', _('Described by')),
    ('describes', _('Describes')),
    ('isPartOf', _('Part of')),
    ('hasPart', _('Has part')),
    ('isReviewedBy', _('Reviewed by')),
    ('reviews', _('Reviews')),
    ('isDocumentedBy', _('Documented by')),
    ('documents', _('Documents')),
    ('compiles', _('Compiles')),
    ('isCompiledBy', _('Compiled by')),
    ('isDerivedFrom', _('Derived from')),
    ('isSourceOf', _('Source of')),
    ('requires', _('Requires')),
    ('isRequiredBy', _('Required by')),
    ('isObsoletedBy', _('Obsoleted by')),
    ('obsoletes', _('Obsoletes')),
    ('isIdenticalTo', _('Identical to')),
]

ZENODO_LOCAL_DOI_PREFIXES = []


ZENODO_DOIID4RECID = {
    7468: 7448,
    7458: 7457,
    7467: 7447,
    7466: 7446,
    7465: 7464,
    7469: 7449,
    7487: 7486,
    7482: 7481,
    7484: 7483,
}
"""Mapping of recids to the id used in generated DOIs.

Wrong DOIs were minted for a short period in 2013 due to mistake in the legacy
system.
"""

ZENODO_CUSTOM_METADATA_TERM_TYPES = {
    'keyword': six.string_types,
    'text': six.string_types,
    'relationship': dict,
}
"""Custom metadata term types mapping."""

ZENODO_CUSTOM_METADATA_VOCABULARIES = {}
"""Custom metadata vocabularies.

..code-block:: python

    ZENODO_CUSTOM_METADATA_VOCABULARIES = {
        'dwc': {
            '@context': 'http://rs.tdwg.org/dwc/terms/',
            'attributes': {
                'family': {'type': 'keyword', 'label': 'Family'},
                'genus': {'type': 'keyword', 'label': 'Genus'},
                'behavior': {'type': 'text', 'label': 'Behaviour'}
            }
        },
        'obo': {
            '@context': 'http://purl.obolibrary.org/obo/',
            'attributes': {
                'RO_0002453': {'type': 'relationship', 'label': 'hostOf'},
            }
        },
    },


"""
