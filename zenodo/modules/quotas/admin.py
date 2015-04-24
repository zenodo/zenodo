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


"""Admin interface to shared links."""


from invenio.base.i18n import _
from invenio.ext.admin.views import ModelView
from invenio.ext.sqlalchemy import db

from .models import ResourceUsage


class ResourceUsageAdmin(ModelView):
    _can_create = False
    _can_edit = False
    _can_delete = False

    acc_view_action = 'cfgquotas'
    acc_edit_action = 'cfgquotas'
    acc_delete_action = 'cfgquotas'

    column_list = (
        'object_type', 'object_id', 'metric', 'value', 'modified',
    )

    column_filters = ['object_type', 'metric']

    column_searchable_list = ['object_type', 'object_id', 'metric']

    column_default_sort = ('modified', True)


def register_admin(app, admin):
    """Called on app initialization to register administration interface."""
    category = _('Quotas')

    admin.add_view(ResourceUsageAdmin(
        ResourceUsage, db.session,
        name=_('Resource Usage'), category=category))
