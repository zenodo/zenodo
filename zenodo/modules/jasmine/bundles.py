# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from invenio.ext.assets import Bundle

jasmine_js = Bundle(
    # es5-shim is needed by PhantomJS
    'vendors/es5-shim/es5-shim.js',
    'vendors/es5-shim/es5-sham.js',
    'vendors/jasmine/lib/jasmine-core/jasmine.js',
    'vendors/jasmine/lib/jasmine-core/jasmine-html.js',
    'vendors/jasmine/lib/jasmine-core/boot.js',
    'vendors/jquery/dist/jquery.js',
    'vendors/jasmine-jquery/lib/jasmine-jquery.js',
    'vendors/jasmine-flight/lib/jasmine-flight.js',
    'vendors/jasmine-ajax/lib/mock-ajax.js',
    output="jasmine.js",
    weight=-1,
    bower={
        "jasmine": ">=2",
        "jasmine-jquery": ">=2",
        "jasmine-flight": ">=3",
        "jasmine-ajax": ">=2",
    }
)

jasmine_styles = Bundle(
    'vendors/jasmine/lib/jasmine-core/jasmine.css',
    weight=-1,
    output='jasmine.css'
)
