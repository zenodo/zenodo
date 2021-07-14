# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017-2018 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

import urllib
import hashlib

from flask import current_app

from zenodo.modules.records.models import ObjectType

from .proxies import current_openaire


class _OAType(object):
    """OpenAIRE types."""

    publication = 'publication'
    dataset = 'dataset'
    software = 'software'
    other = 'other'


def is_openaire_publication(record):
    """Determine if record is a publication for OpenAIRE."""
    oatype = ObjectType.get_by_dict(record.get('resource_type')).get(
        'openaire', {})
    if not oatype or oatype['type'] != _OAType.publication:
        return False

    # Has grants, is part of ecfunded community or is open access.
    if record.get('grants') or 'ecfunded' in record.get('communities', []) or \
            'open' == record.get('access_right'):
        return True
    return False


def is_openaire_dataset(record):
    """Determine if record is a dataset for OpenAIRE."""
    oatype = ObjectType.get_by_dict(record.get('resource_type')).get(
        'openaire', {})
    return oatype and oatype['type'] == _OAType.dataset


def is_openaire_software(record):
    """Determine if the record is a software for OpenAIRE."""
    oatype = ObjectType.get_by_dict(record.get('resource_type')).get(
        'openaire', {})
    return oatype and oatype['type'] == _OAType.software


def is_openaire_other(record):
    """Determine if the record has type 'other' for OpenAIRE."""
    oatype = ObjectType.get_by_dict(record.get('resource_type')).get(
        'openaire', {})
    return oatype and oatype['type'] == _OAType.other


def openaire_type(record):
    """Get the OpenAIRE type of a record."""
    if is_openaire_publication(record):
        return _OAType.publication
    elif is_openaire_dataset(record):
        return _OAType.dataset
    elif is_openaire_software(record):
        return _OAType.software
    elif is_openaire_other(record):
        return _OAType.other
    return None


def openaire_id(record):
    """Compute the OpenAIRE identifier."""
    return _openaire_id(record, openaire_type(record))


def _openaire_id(record, oatype):
    """Compute the OpenAIRE identifier."""
    prefix, identifier = openaire_original_id(record, oatype)

    if not identifier or not prefix:
        return None

    m = hashlib.md5()
    m.update(identifier.encode('utf8'))

    return '{}::{}'.format(prefix, m.hexdigest())


def openaire_datasource_id(record):
    """Get OpenAIRE datasource identifier."""
    return current_app.config['OPENAIRE_ZENODO_IDS'].get(openaire_type(record))


def openaire_original_id(record, oatype):
    """Original original identifier."""
    prefix = current_app.config['OPENAIRE_NAMESPACE_PREFIXES'].get(oatype)

    value = None
    if oatype == _OAType.publication or oatype == _OAType.software or \
        oatype == _OAType.other:
        value = record.get('_oai', {}).get('id')
    elif oatype == _OAType.dataset:
        value = record.get('doi')

    return prefix, value


def openaire_link(record):
    """Compute an OpenAIRE link."""
    oatype = openaire_type(record)
    doi = record.get('doi')

    if oatype == _OAType.publication:
        return '{}/search/publication?pid={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            urllib.quote(doi),
        )
    elif oatype == _OAType.dataset:
        return '{}/search/dataset?pid={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            urllib.quote(doi),
        )
    elif oatype == _OAType.software:
        return '{}/search/software?pid={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            urllib.quote(doi),
        )
    elif oatype == _OAType.other:
        return '{}/search/other?pid={}'.format(
            current_app.config['OPENAIRE_PORTAL_URL'],
            urllib.quote(doi),
        )
    return None


def resolve_openaire_communities(communities):
    """Resolve a Zenodo communities list to an OpenAIRE communities set."""
    openaire_comms = set()
    for comm in communities:
        oa_comms = current_openaire.inverse_openaire_community_map.get(comm)
        if oa_comms:
            for oa_comm in oa_comms:
                openaire_comms.add(oa_comm)
    return openaire_comms


def openaire_community_identifier(openaire_community):
    """Get OpenAIRE community identifier."""
    return u'{0}/{1}'.format(
        current_app.config['OPENAIRE_COMMUNITY_IDENTIFIER_PREFIX'],
        openaire_community)
