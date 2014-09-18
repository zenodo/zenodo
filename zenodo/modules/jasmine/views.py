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

from flask import Blueprint, render_template, send_file, abort, url_for
from .registry import specs

blueprint = Blueprint(
    'zenodo_jasmine',
    __name__,
    url_prefix='/jasmine',
    static_folder='static',
    template_folder='templates'
)


@blueprint.route('/specrunner/', methods=['GET'])
def specrunner():
    modules = [url_for('zenodo_jasmine.spec', specpath=x) for x in specs.keys()]
    modules.sort()
    return render_template('jasmine/specrunner.html', modules=modules)


@blueprint.route('/spec/<path:specpath>', methods=['GET'])
def spec(specpath):
    """Send a single spec file."""
    if specpath not in specs:
        abort(404)

    return send_file(
        specs[specpath],
        mimetype="application/javascript",
        conditional=False,
        add_etags=False,
    )
