# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2014 CERN.
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

from __future__ import absolute_import
from flask import Blueprint, render_template
from flask.ext.menu import register_menu
from flask.ext.breadcrumbs import register_breadcrumb
from invenio.base.i18n import _

blueprint = Blueprint(
    'preservationmeter',
    __name__,
    url_prefix="",
    static_folder='static',
    template_folder='templates',
)


@blueprint.route('/preservation-best-practice', methods=['GET', ])
@register_menu(blueprint, 'main.getstarted.preservation',
               _('Preservation Best Practice'), order=9)
@register_breadcrumb(blueprint, 'breadcrumbs.preservation',
                     _("Preservation Best Practice"))
def preservation_best_practice():
    return render_template('preservationmeter/preservation_best_practice.html')
