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

"""Configuration for ZenodoOpenAIRE."""

from __future__ import absolute_import, print_function

ZENODO_OPENAIRE_SUBTYPES = {
    'openaire_communities': {
        'dh-ch': [
            'adho',
            'archaeology',
            'chc',
            'crosscult',
            'digcur2013',
            'digitalhumanities',
            'dimpo',
            'dipp2014',
            'gravitate',
            'storm',
            'wahr',
            'wholodance_eu'
        ],
        'fam': [
            'adriplan',
            'aquatrace',
            'fisheries',
            'myfish',
            'proeel',
            'sedinstcjfas'
        ],
        'mes': [
            'devotes-project',
            'sponges'
        ],
        'ni': [
            'neuroinformatics'
        ]
    },
    'openaire_types': {
        'software': {
            'mes': [
                {'id': 'mes:statistical-procedure', 'name': 'Statistical procedure'},
                {'id': 'mes:software-pipeline', 'name': 'Software pipeline'},
                {'id': 'mes:web-service', 'name': 'Web Service'},
            ],
            'dh-ch': [
            ],
            'ni': [
                {'id': 'ni:image-processing-software', 'name': 'Image processing software'},
            ],
            'fam': [
                {'id': 'fam:online-compilation-environment', 'name': 'Online Compilation Environment'},
                {'id': 'fam:processing', 'name': 'Processing'},
                {'id': 'fam:easterizations', 'name': 'Rasterizations'},
                {'id': 'fam:format-transformation-or-mapping', 'name': 'Format transformation or mapping'},
            ],
            'icre8-sdsn-greece': [
                {'id': 'icre8-sdsn-greece:data-processing', 'name': 'Data Processing'},
                {'id': 'icre8-sdsn-greece:syntax-files', 'name': 'Syntax files'},
                {'id': 'icre8-sdsn-greece:data-analysis', 'name': 'Data analysis'},
                {'id': 'icre8-sdsn-greece:data-visualization', 'name': 'Data Visualization'},
            ],
        },
        'other': {
            'mes': [
                {'id': 'mes:laboratory-procedure', 'name': 'Laboratory procedure'},
                {'id': 'mes:aggregated-data', 'name': 'Aggregated Data'},
                {'id': 'mes:manual-aggregation-of-data-sets', 'name': 'Manual aggregation of data sets'},
            ],
            'dh-ch': [
            ],
            'ni': [
                {'id': 'ni:workflow-pipeline', 'name': 'Workflow Pipeline'},
                {'id': 'ni:vip-pipeline-template', 'name': 'VIP pipeline template'},
                {'id': 'ni:vip-pipeline-challenge-dataset-results', 'name': 'VIP pipeline Challenge -Dataset Results'},
                {'id': 'ni:images-and-associated-metadata', 'name': 'Images and associated metadata'},
            ],
            'fam': [
                {'id': 'fam:etl-extract-transform-load', 'name': 'ETL (Extract, Transform, Load)'},
                {'id': 'fam:model', 'name': 'Model'},
                {'id': 'fam:dryad-data-package', 'name': 'Dryad data package'},
            ],
            'icre8-sdsn-greece': [
            ],
        },
    }
}
"""OpenAIRE subtypes configuration."""
