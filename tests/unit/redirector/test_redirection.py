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

"""Zenodo redirector tests."""

from __future__ import absolute_import, print_function

from flask import url_for

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs


def compare_url(url, expected):
    """Compare two urls replying if they are the same."""
    def get_querystring_dict(url):
        return parse_qs(urlparse(url).query)
    return (get_querystring_dict(url) == get_querystring_dict(expected) and
            urlparse(url).path == urlparse(expected).path)


def check_redirection(response, expected_url):
    """."""
    assert response.status_code == 302
    assert compare_url(response.headers['Location'], expected_url)


def test_redirection_community(app_client, db):
    """Check the redirection using a direct translation."""
    url_redirection = url_for('invenio_communities.detail', community_id=1,
                              _external=True)

    response = app_client.get('/collection/user-1')
    check_redirection(response, url_redirection)


def test_redirection_community_search(app_client):
    """Check the redirection using a direct translation."""
    url_redirection = url_for('invenio_communities.search', community_id=1,
                              _external=True)

    response = app_client.get('/search?cc=user-1')
    check_redirection(response, url_redirection)

    # Query translation
    url_redirection = url_for('invenio_communities.search', community_id=1,
                              q='test', _external=True)

    response = app_client.get('/search?cc=user-1&p=test')
    check_redirection(response, url_redirection)


def test_redirection_communities_provisional_user(app_client):
    """Check the redirection using a direct translation."""
    url_redirection = url_for('invenio_communities.curate', community_id=1,
                              _external=True)

    response = app_client.get('/search?cc=provisional-user-1')
    check_redirection(response, url_redirection)

    # Query translation
    url_redirection = url_for('invenio_communities.curate', community_id=1,
                              q='test', _external=True)

    response = app_client.get('/search?cc=provisional-user-1&p=test')
    check_redirection(response, url_redirection)


def test_redirection_communities_about(app_client):
    """Check the redirection using a direct translation."""
    url_redirection = url_for('invenio_communities.about', community_id=1,
                              _external=True)

    response = app_client.get('/communities/about/1/')
    check_redirection(response, url_redirection)


def test_redirection_collections_type(app_client):
    """Check the redirection using a direct translation."""
    # Type
    url_redirection = url_for('invenio_search_ui.search', type='video',
                              _external=True)
    response = app_client.get('/collection/videos')
    check_redirection(response, url_redirection)

    # Type and subtype
    url_redirection = url_for('invenio_search_ui.search', type='publication',
                              subtype='deliverable', _external=True)
    response = app_client.get('/collection/deliverable')
    check_redirection(response, url_redirection)


def test_redirection_collections_search(app_client):
    """Check the redirection using a direct translation."""
    # Type
    url_redirection = url_for('invenio_search_ui.search', type='video',
                              _external=True)
    response = app_client.get('/search?cc=videos')
    check_redirection(response, url_redirection)

    # Type and subtype
    url_redirection = url_for('invenio_search_ui.search', type='publication',
                              subtype='deliverable', _external=True)
    response = app_client.get('/search?cc=deliverable')
    check_redirection(response, url_redirection)

    # Query translation
    url_redirection = url_for('invenio_search_ui.search', type='publication',
                              subtype='deliverable', q='test', _external=True)

    response = app_client.get('/search?cc=deliverable&p=test')
    check_redirection(response, url_redirection)


def test_redirection_search_behaviour(app_client):
    """Check the behaviour of url_for using invenio_search_ui.index."""
    # Empty url
    response = app_client.get(url_for('invenio_search_ui.search'))
    assert response.status_code == 200
    assert '<invenio-search' in response.get_data(as_text=True)

    # Query string
    response = app_client.get(url_for('invenio_search_ui.search',
                                      page=1, size=20, q='Aa'))
    assert response.status_code == 200
    assert '<invenio-search' in response.get_data(as_text=True)
