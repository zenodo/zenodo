# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Bundles for Zenodo deposit form."""

from flask_assets import Bundle
from invenio_assets import NpmBundle
from invenio_deposit.bundles import js_dependecies_autocomplete, \
    js_dependecies_schema_form, js_dependecies_uploader, \
    js_dependencies_ckeditor, js_dependencies_jquery, \
    js_dependencies_ui_sortable, js_main

js_zenodo_deposit = Bundle(
    'js/zenodo_deposit/filters.js',
    'js/zenodo_deposit/directives.js',
    'js/zenodo_deposit/controllers.js',
    'js/zenodo_deposit/providers.js',
    'js/zenodo_deposit/config.js',
    depends=(
        'js/zenodo_deposit/*.js',
    ),
)


js_deposit = NpmBundle(
    js_dependencies_jquery,
    js_main,
    js_dependecies_uploader,
    js_dependecies_schema_form,
    js_dependecies_autocomplete,
    js_dependencies_ui_sortable,
    js_dependencies_ckeditor,
    js_zenodo_deposit,
    filters='uglifyjs',
    output='gen/zenodo.deposit.%(version)s.js',
)
