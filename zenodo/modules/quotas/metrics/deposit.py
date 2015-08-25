# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Deposit disk usage metrics per user."""

from __future__ import absolute_import

from invenio.modules.deposit.models import Deposition

from ..models import Metric


class DepositMetric(Metric):

    """Number of deposits and file storage per user."""

    metric_class = "deposit"
    object_type = "User"

    @classmethod
    def all(cls):
        """Compute deposit metrics per user."""
        data = dict()

        for d in Deposition.get_depositions():
            if str(d.user_id) not in data:
                data[str(d.user_id)] = dict(num=0, size=0, files=0)

            # Count number of deposits
            data[str(d.user_id)]['num'] += 1

            # Collected file sizes
            for f in d.files:
                data[str(d.user_id)]['size'] += f.size
                data[str(d.user_id)]['files'] += 1

        return data.items()
