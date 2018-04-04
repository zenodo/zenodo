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

"""Redirects for legacy URLs."""

from __future__ import absolute_import, print_function, unicode_literals

from flask import Blueprint, abort, current_app
from invenio_cache import current_cache

blueprint = Blueprint(
    'zenodo_sitemap',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)

def _get_cached_or_404(page):
    data =  current_cache.get('sitemap:' + str(page))
    if data:
        return current_app.response_class(data, mimetype='text/xml')
    else:
        abort(404)

@blueprint.route('/sitemap.xml', methods=['GET', ])
def sitemapindex():
    """Get the sitemap index."""
    return _get_cached_or_404(0)


@blueprint.route('/sitemap<int:page>.xml', methods=['GET', ])
def sitemappage(page):
    """Get the sitemap page."""
    return _get_cached_or_404(page)
