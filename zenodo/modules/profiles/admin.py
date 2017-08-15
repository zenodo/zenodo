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

"""Admin views for Zenodo Profiles."""

from flask_admin.contrib.sqla import ModelView

from zenodo.modules.profiles.models import Profile


def _(x):
    """Identity."""
    return x


class ProfileView(ModelView):
    """Profiles view."""

    can_view_details = True
    can_delete = False

    column_list = (
        'user_id',
        'bio',
        'affiliation',
        'location',
        'website',
        'show_profile',
        'allow_contact_owner'
    )

    form_columns = \
        column_searchable_list = \
        column_filters = \
        column_details_list = \
        columns_sortable_list = \
        column_list


researcher_profile_adminview = {
    'model': Profile,
    'modelview': ProfileView,
    'category': _('User Management'),
}
