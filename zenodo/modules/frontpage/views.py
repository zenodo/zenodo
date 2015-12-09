# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo frontpage blueprint."""

from __future__ import absolute_import, print_function

from flask import Blueprint, render_template, flash
from flask_menu import register_menu

blueprint = Blueprint(
    'zenodo_frontpage',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/')
@register_menu(blueprint, 'main.index', 'Search', order=1)
def index():
    """Frontpage blueprint."""
    flash('Just a test.', category='info')
    return render_template('zenodo_theme/page.html')


@blueprint.route('/2')
@register_menu(blueprint, 'main.search', 'Upload', order=2)
def index2():
    """Frontpage blueprint."""
    return render_template('zenodo_theme/page.html')


@blueprint.route('/3')
@register_menu(blueprint, 'main.communities', 'Communities', order=3)
def index3():
    """Frontpage blueprint."""
    return render_template('zenodo_theme/page.html')
