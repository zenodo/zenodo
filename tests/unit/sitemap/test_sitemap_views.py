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

"""Test Sitemap views."""

from __future__ import absolute_import, print_function

import mock
from flask import current_app, render_template, url_for
from invenio_cache import current_cache

from zenodo.modules.sitemap.tasks import update_sitemap_cache


def test_sitemap_templates(app):
    """Test Sitemap views."""
    min_urlset = [
        {
            'loc': 'https://zenodo.org/record/1',
        }
    ]
    page = render_template('zenodo_sitemap/sitemap.xml', urlset=min_urlset)
    assert '<loc>https://zenodo.org/record/1</loc>' in page

    full_urlset = [
        {
            'loc': 'https://zenodo.org/record/1',
            'lastmod': '2018-01-01',
            'changefreq': '1',
            'priority': '10',
        }
    ]
    page = render_template('zenodo_sitemap/sitemap.xml', urlset=full_urlset)
    assert '<loc>https://zenodo.org/record/1</loc>' in page
    assert '<lastmod>2018-01-01</lastmod>' in page
    assert '<changefreq>1</changefreq>' in page
    assert '<priority>10</priority>' in page

    def make_url(loc):
        return {'loc': 'https://zenodo.org' + loc}

    sitemapindex = [make_url('/sitemap{}.xml'.format(i)) for i in range(1, 4)]
    page = render_template('zenodo_sitemap/sitemapindex.xml',
                           urlset=sitemapindex, url_scheme='https')
    assert '<loc>https://zenodo.org/sitemap1.xml</loc>' in page
    assert '<loc>https://zenodo.org/sitemap2.xml</loc>' in page
    assert '<loc>https://zenodo.org/sitemap3.xml</loc>' in page
    # Some sanity checks
    assert '<loc>https://zenodo.org/sitemap0.xml</loc>' not in page
    assert '<loc>https://zenodo.org/sitemap4.xml</loc>' not in page
    assert '<loc>https://zenodo.org/sitemap.xml</loc>' not in page


def test_sitemap_views(app, record_with_bucket, communities):
    """Test the sitemap views."""
    with app.test_request_context():
        with app.test_client() as client:
            res = client.get(url_for('zenodo_sitemap.sitemapindex'))
            # Return 404 if sitemap has not been generated
            assert res.status_code == 404

            res = client.get(url_for('zenodo_sitemap.sitemappage', page=1))
            # Return 404 if sitemap has not been generated
            assert res.status_code == 404

            update_sitemap_cache()
            res = client.get(url_for('zenodo_sitemap.sitemapindex'))
            assert res.status_code == 200
            res = client.get(url_for('zenodo_sitemap.sitemappage', page=1))
            assert res.status_code == 200

            # Clear the cache to clean up after test
            sitemap = current_app.extensions['zenodo-sitemap']
            sitemap.clear_cache()
