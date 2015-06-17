# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013 CERN.
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

"""PIDStore metrics."""

from __future__ import absolute_import

from flask import current_app

from invenio.modules.pidstore.models import PersistentIdentifier

from zenodo.modules.quotas.models import Metric


class PIDStoreMetric(Metric):

    """Aggregated metrics for pidstore."""

    metric_class = "pidstore"
    object_type = "System"

    @classmethod
    def all(cls):
        """Compute bibsched queue length."""
        system_name = current_app.config.get('CFG_SITE_NAME', 'Invenio')
        dois = PersistentIdentifier.query.filter_by(pid_type='doi',
                                                    status='R').count()
        data = {system_name: {
            'numdois': dois,
        }}
        return data.items()
