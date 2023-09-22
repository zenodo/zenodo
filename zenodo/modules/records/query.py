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

"""Configuration for Zenodo Records search."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl import Q
from flask import current_app, request
from invenio_records_rest.query import es_search_factory as _es_search_factory


def apply_version_filters(search, urlkwargs):
    """Apply record version filters to search."""
    if 'all_versions' in request.values:
        all_versions = request.values['all_versions']
        if str(all_versions).lower() in ("", "1", "true"):
            urlkwargs.add('all_versions', "true")
        else:
            urlkwargs.add('all_versions', str(request.values['all_versions']))
            search = search.filter(Q('term', **{'relations.version.is_last': True}))
    else:
        search = search.filter(Q('term', **{'relations.version.is_last': True}))
    return (search, urlkwargs)

def apply_safelist_filter(search, urlkwargs):
    """Apply safelist filter to search."""
    safelist_filter_enabled = current_app.config.get(
        'ZENODO_RECORDS_SEARCH_SAFELIST', False)
    has_query = urlkwargs.get('q')
    if safelist_filter_enabled and not has_query:
        # Include if safelisted or undetermined (i.e. not indexed yet)
        search = search.filter(
            Q('term', _safelisted=True) | ~Q('exists', field='_safelisted')
        )

    return (search, urlkwargs)


def search_factory(self, search, query_parser=None):
    """Search factory."""
    search, urlkwargs = _es_search_factory(self, search)
    return apply_safelist_filter(*apply_version_filters(search, urlkwargs))
