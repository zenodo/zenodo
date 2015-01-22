# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
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

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2


def create_badge(text, output_path, style=None):
    """Retrieve an SVG DOI badge from shields.io."""
    text = text.replace('/', '%2F')
    options = ""
    if style == "flat":
        options = "?style=flat"
    elif style == "flat-square":
        options = "?style=flat-square"
    elif style == "plastic":
        options = "?style=plastic"

    response = urllib2.urlopen(
        'http://img.shields.io/badge/DOI-%s-blue.svg%s' % (text, options))

    with open(output_path, 'wb') as f:
        f.write(response.read())
