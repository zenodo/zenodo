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

"""Forms for spam deletion module."""

from __future__ import absolute_import, print_function

from flask_babelex import lazy_gettext as _
from flask_wtf import Form
from wtforms import BooleanField, SubmitField


class DeleteSpamForm(Form):
    """Form for deleting spam."""

    remove_all_communities = BooleanField(
        _('Remove the user communities?'),
        default=True,
        description=_('Will remove all communities owned by the user.'),
    )

    remove_all_records = BooleanField(
        _('Remove all user records?'),
        default=True,
        description=_('Will remove all records owned by the user.'),
    )

    deactivate_user = BooleanField(
        _('Deactivate the user account?'),
        default=True,
        description=_('Will deactivate the user account.'),
    )

    delete = SubmitField(_("Permanently delete"))
