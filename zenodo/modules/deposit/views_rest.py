# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

from __future__ import absolute_import, print_function

from flask import Blueprint, jsonify, request
from flask_security import login_required

from .utils import suggest_language

blueprint = Blueprint(
    'zenodo_deposit',
    __name__,
    url_prefix='',
)


@blueprint.route(
    '/language/',
    methods=['GET']
)
@login_required
def language():
    """Suggest a language on the deposit form."""
    q = request.args.get('q', '')
    limit = int(request.args.get('limit', '5').lower())
    langs = suggest_language(q, limit=limit)
    langs = [{'code': l.alpha_3, 'name': l.name} for l in langs]
    d = {
        'suggestions': langs
    }
    return jsonify(d)
