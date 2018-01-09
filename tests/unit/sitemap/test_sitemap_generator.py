# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Test API for Zenodo and GitHub integration."""

from __future__ import absolute_import, print_function

import mock
from flask import current_app, render_template

from zenodo.modules.sitemap.tasks import update_sitemap_cache


def test_sitemap_cache_update_simple(mocker, app):
    """Test Sitemap cache updating with fixed parameters."""
    def make_url(loc):
        return {'loc': 'https://zenodo.org' + loc}

    urls = [make_url('/record/' + str(i)) for i in range(5)]
    cache_mock = mocker.patch('zenodo.modules.sitemap.ext.current_cache')
    update_sitemap_cache(urls=urls, max_url_count=2)

    sitemap1 = render_template('zenodo_sitemap/sitemap.xml',
                               urlset=urls[:2])
    cache_mock.set.assert_any_call('sitemap:1', sitemap1)

    sitemap2 = render_template('zenodo_sitemap/sitemap.xml',
                               urlset=urls[2:4])
    cache_mock.set.assert_any_call('sitemap:2', sitemap2)

    sitemap3 = render_template('zenodo_sitemap/sitemap.xml',
                               urlset=urls[4:])
    cache_mock.set.assert_any_call('sitemap:3', sitemap3)

    sitemapindex = [make_url('/sitemap{}.xml'.format(i)) for i in range(1, 4)]
    sitemap0 = render_template('zenodo_sitemap/sitemapindex.xml',
                               urlset=sitemapindex, url_scheme='https')
    cache_mock.set.assert_any_call('sitemap:0', sitemap0)


def test_sitemap_generators(app, record_with_bucket, communities):
    """Test Sitemap generators."""
    with app.test_request_context():
        sitemap = current_app.extensions['zenodo-sitemap']
        urls = list(sitemap._generate_all_urls())

        # Make sure the last modified are there, but remove from the result
        # for easier comparison of URLs
        assert all('lastmod' in url for url in urls)
        for url in urls:
            del url['lastmod']
        expected = [
            {'loc': 'https://localhost/record/12345'},
            {'loc': 'https://localhost/communities/c1/'},
            {'loc': 'https://localhost/communities/c1/search'},
            {'loc': 'https://localhost/communities/c1/about/'},
            {'loc': 'https://localhost/communities/c2/'},
            {'loc': 'https://localhost/communities/c2/search'},
            {'loc': 'https://localhost/communities/c2/about/'},
            {'loc': 'https://localhost/communities/c3/'},
            {'loc': 'https://localhost/communities/c3/search'},
            {'loc': 'https://localhost/communities/c3/about/'},
            {'loc': 'https://localhost/communities/c4/'},
            {'loc': 'https://localhost/communities/c4/search'},
            {'loc': 'https://localhost/communities/c4/about/'},
            {'loc': 'https://localhost/communities/c5/'},
            {'loc': 'https://localhost/communities/c5/search'},
            {'loc': 'https://localhost/communities/c5/about/'},
            {'loc': 'https://localhost/communities/zenodo/'},
            {'loc': 'https://localhost/communities/zenodo/search'},
            {'loc': 'https://localhost/communities/zenodo/about/'},
            {'loc': 'https://localhost/communities/ecfunded/'},
            {'loc': 'https://localhost/communities/ecfunded/search'},
            {'loc': 'https://localhost/communities/ecfunded/about/'},
            {'loc': 'https://localhost/communities/grants_comm/'},
            {'loc': 'https://localhost/communities/grants_comm/search'},
            {'loc': 'https://localhost/communities/grants_comm/about/'}
        ]
        assert urls == expected
