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

"""Test for OpenAIRE helpers."""

from __future__ import absolute_import, print_function

from zenodo.modules.openaire.helpers import openaire_id, openaire_link, \
    openaire_type


def test_openire_type(app, minimal_record):
    """Test OpenAIRE type."""
    r = minimal_record
    # Default zenodo type is software which has no OpenAIRE type.
    assert openaire_type(r) is None

    # Datasets just map to datasets.
    r['resource_type']['type'] = 'dataset'
    assert openaire_type(r) == 'dataset'

    # Open publications
    r['resource_type']['type'] = 'publication'
    assert openaire_type(r) == 'publication'

    # Non-open publications
    r['access_right'] = 'embargoed'
    assert openaire_type(r) is None
    # with grants
    r['grants'] = [{'id': 'someid'}]
    assert openaire_type(r) == 'publication'

    # in ecfunded community
    del r['grants']
    r['communities'] = ['ecfunded']
    assert openaire_type(r) == 'publication'
    r['communities'] = ['zenodo']
    assert openaire_type(r) is None


def test_openire_id(app, minimal_record):
    """Test OpenAIRE ID."""
    r = minimal_record
    r['doi'] = u'10.5281/zenodo.123'
    r['_oai'] = {'id': u'oai:zenodo.org:123'}

    # Default zenodo type is software which has no OpenAIRE type.
    assert openaire_id(r) is None

    # Dataset ID
    r['resource_type']['type'] = 'dataset'
    assert openaire_id(r) == 'r37b0ad08687::204007f516ddcf0a452c2f22d48695ca'

    # Publication ID
    r['resource_type']['type'] = 'publication'
    assert openaire_id(r) == 'od______2659::47287d1800c112499a117ca17aa1909d'


def test_openire_link(app, minimal_record):
    """Test OpenAIRE ID."""
    r = minimal_record
    r['doi'] = u'10.5281/zenodo.123'
    r['_oai'] = {'id': u'oai:zenodo.org:123'}

    # Default zenodo type is software which has no OpenAIRE type.
    assert openaire_link(r) is None

    # Dataset ID
    r['resource_type']['type'] = 'dataset'
    assert openaire_link(r) == \
        'https://beta.openaire.eu/search/dataset' \
        '?datasetId=r37b0ad08687::204007f516ddcf0a452c2f22d48695ca'

    # Publication ID
    r['resource_type']['type'] = 'publication'
    assert openaire_link(r) == \
        'https://beta.openaire.eu/search/publication' \
        '?articleId=od______2659::47287d1800c112499a117ca17aa1909d'
