# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Pages bundles."""

from invenio.base.bundles import invenio as _i, jquery as _j
from invenio.ext.assets import Bundle, RequireJSFilter

guide_js = Bundle(
    "js/pages/guide.js",
    output="guide.js",
    filters=RequireJSFilter(exclude=[_j, _i]),
    weight=51,
    bower={
        "jquery.pin": "latest",
    }
)

guide_css = Bundle(
    "css/pages/guide.less",
    output="guide.css",
    filters="less, cleancss",
    weight=51,
)

page_list_css = Bundle(
    "css/pages/list.less",
    output="list.css",
    filters="less, cleancss",
    weight=51,
)
