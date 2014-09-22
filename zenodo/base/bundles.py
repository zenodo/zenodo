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

"""Zenodo base bundles."""

from invenio.base.bundles import styles as _s, jquery as _j, invenio as _i

#
# Site-wide JS
#
_i.contents += [
    "js/zenodo/init.js",
]

_j.contents += [
    "vendors/zeroclipboard/dist/ZeroClipboard.js",
    "vendors/bootstrap-datepicker/js/bootstrap-datepicker.js",
    "vendors/bootstrap-switch/dist/js/bootstrap-switch.min.js",
    "js/citationformatter/citationformatter.js",
]

_j.bower.update({
    "zeroclipboard": "~2.1.6",
    "bootstrap-datepicker": "latest",
    "bootstrap-switch": "3.0.2",
})
# Remove MathJax (served from CDN instead).
del _j.bower['MathJax']

#
# Site-wide styles
#
_s.contents.remove("less/base.less")
_s.contents.remove("less/footer.less")
_s.contents += [
    "less/zenodo.less",
]
