# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""OpenAIRE related helpers."""

from __future__ import absolute_import, print_function

import hashlib

from flask import current_app


class _OAType(object):
    """OpenAIRE types."""

    publication = 'publication'
    dataset = 'dataset'


def is_openaire_publication(record):
    """Determine if record is a publication for OpenAIRE."""
    types = ['publication', 'presentation', 'poster']
    if record.get('resource_type', {}).get('type') not in types:
        return False

    # Has grants, is part of ecfunded community or is open access.
    if record.get('grants') or 'ecfunded' in record.get('communities', []) or \
            'open' == record.get('access_right'):
        return True
    return False


def is_openaire_dataset(record):
    """Determine if record is a dataset for OpenAIRE."""
    if record.get('resource_type', {}).get('type') == 'dataset':
        return True
    return False


def openaire_type(record):
    """Get the OpenAIRE type of a record."""
    if is_openaire_publication(record):
        return _OAType.publication
    elif is_openaire_dataset(record):
        return _OAType.dataset
    return None


def openaire_id(record):
    """Compute the OpenAIRE identifier."""
    return _openaire_id(record, openaire_type(record))


def _openaire_id(record, oatype):
    """Compute the OpenAIRE identifier."""
    prefix = None
    value = None
    if oatype == _OAType.publication:
        # Hard-coded prefix from OpenAIRE.
        prefix = current_app.config['OPENAIRE_ID_PREFIX_PUBLICATION']
        value = record.get('_oai', {}).get('id')
    elif oatype == _OAType.dataset:
        # Hard-coded prefix from OpenAIRE.
        prefix = current_app.config['OPENAIRE_ID_PREFIX_DATASET']
        value = record.get('doi')

    if not value or not prefix:
        return None

    m = hashlib.md5()
    m.update(value.encode('utf8'))

    return '{}::{}'.format(prefix, m.hexdigest())


def openaire_link(record):
    """Compute an OpenAIRE link."""
    oatype = openaire_type(record)
    oaid = _openaire_id(record, oatype)

    if oatype == _OAType.publication:
        return '{}/search/publication?articleId={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            oaid,
        )
    elif oatype == _OAType.dataset:
        return '{}/search/dataset?datasetId={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            oaid,
        )
    return None
