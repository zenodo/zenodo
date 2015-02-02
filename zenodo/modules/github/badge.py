# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2014, 2015 CERN.
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

"""Utility module to create badge."""

from six.moves.urllib import parse, request

from invenio.base.globals import cfg


def shieldsio_encode(text):
    """Encode text for shields.io."""
    return parse.quote_plus(text.replace('-', '--').replace('_', '__'))


def create_badge(subject, status, color, output_path, style=None):
    """Retrieve an SVG DOI badge from shields.io."""
    subject = shieldsio_encode(subject)
    status = shieldsio_encode(status)

    if style not in cfg["GITHUB_BADGE_STYLES"]:
        style = cfg["GITHUB_BADGE_DEFAULT_STYLE"]
    if color not in cfg["GITHUB_BADGE_COLORS"]:
        color = cfg["GITHUB_BADGE_DEFAULT_COLOR"]

    options = "?{}".format(parse.urlencode(dict(style=style)))

    url = '{url}{subject}-{status}-{color}.svg{style}'.format(
        url=cfg['GITHUB_SHIELDSIO_BASE_URL'],
        subject=subject,
        status=status,
        color=color,
        style=options,
    )

    response = request.urlopen(url)

    with open(output_path, 'wb') as f:
        f.write(response.read())
