# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""JS/CSS bundles for theme."""

from __future__ import absolute_import, print_function

from flask_assets import Bundle
from invenio_assets import NpmBundle

css = NpmBundle(
    Bundle(
        'scss/styles.scss',
        filters='scss, cleancss',
    ),
    Bundle(
        'node_modules/angular-loading-bar/build/loading-bar.css',
        'node_modules/typeahead.js-bootstrap-css/typeaheadjs.css',
        filters='cleancss',
    ),
    depends=('scss/*.scss', ),
    output='gen/zenodo.%(version)s.css',
    npm={
        'almond': '~0.3.1',
        'bootstrap-sass': '~3.3.5',
        'font-awesome': '~4.4.0',
        'typeahead.js-bootstrap-css': '~1.2.1'
    }
)
"""Default CSS bundle."""

js = NpmBundle(
    Bundle(
        'node_modules/almond/almond.js',
        'js/modernizr-custom.js',
        filters='uglifyjs',
    ),
    Bundle(
        'js/zenodo.js',
        filters='requirejs',
    ),
    depends=(
        'js/zenodo.js',
        'js/zenodo/*.js',
        'js/zenodo/filters/*.js',
        'node_modules/angular-loading-bar/build/*.js',
        'node_modules/typeahead.js/dist/*.js',
        'node_modules/invenio-csl-js/dist/*.js',
    ),
    filters='jsmin',
    output="gen/zenodo.%(version)s.js",
    npm={
        'almond': '~0.3.1',
        'angular': '~1.4.9',
        'angular-sanitize': '~1.4.9',
        'angular-loading-bar': '~0.9.0',
        'invenio-csl-js': '~0.1.2',
        'typeahead.js': '~0.11.1',
    }
)
"""Default JavaScript bundle."""

search_js = NpmBundle(
    Bundle(
        'js/zenodo.search.js',
        filters='requirejs',
    ),
    depends=(
        'node_modules/invenio-search-js/dist/*.js',
        'js/invenio_communities/*.js',
        'js/invenio_communities/directives/*.js',
    ),
    filters='jsmin',
    output="gen/zenodo.search.%(version)s.js",
    npm={
        'clipboard': '1.5.12',
        'invenio-search-js': '~0.2.0',
    }
)
"""Search JavaScript bundle (with communities support)."""
