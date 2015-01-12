# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""Unit tests for citation formatter views."""

from __future__ import absolute_import

from flask import url_for
import httpretty
from invenio.testsuite import InvenioTestCase, make_test_suite, \
    run_test_suite


class CitationFormatterTest(InvenioTestCase):

    """Test citationformatter."""

    @property
    def config(self):
        return dict(
            # HTTPretty doesn't play well with Redis.
            # See gabrielfalcao/HTTPretty#110
            CACHE_TYPE='simple',
            CITATIONFORMATTER_API='http://example.org/citeproc/format'
        )

    @httpretty.activate
    def test_format(self):
        httpretty.register_uri(
            httpretty.GET,
            self.app.config['CITATIONFORMATTER_API'],
            body='my formatted citation',
            content_type="text/plain"
        )

        r = self.client.get(
            url_for('zenodo_citationformatter.format',
                    doi='10.1234/foo.bar', lang='en-US', style='apa')
        )
        self.assert200(r)
        self.assertEqual(r.data, 'my formatted citation')

    def test_format_invalid_params(self):
        r = self.client.get(
            url_for('zenodo_citationformatter.format',
                    doi='invalid-doi', lang='en-US', style='apa')
        )
        self.assert404(r)

        r = self.client.get(
            url_for('zenodo_citationformatter.format',
                    doi='10.1234/foo.bar', lang='invalidlocale', style='apa')
        )
        self.assert404(r)

        r = self.client.get(
            url_for('zenodo_citationformatter.format',
                    doi='10.1234/foo.bar', lang='en-US', style='invalidstyle')
        )
        self.assert404(r)

    @httpretty.activate
    def test_format_api_notfound(self):
        httpretty.register_uri(
            httpretty.GET,
            self.app.config['CITATIONFORMATTER_API'],
            body='DOI not found',
            content_type="text/plain",
            status=404,
        )

        r = self.client.get(
            url_for('zenodo_citationformatter.format',
                    doi='10.1234/foo.bar', lang='en-US', style='apa')
        )
        self.assert404(r)


TEST_SUITE = make_test_suite(CitationFormatterTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
