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


from flask_registry import ImportPathRegistry, RegistryProxy, RegistryError

from invenio.base.globals import cfg

from .models import Metric


class MetricsRegistry(ImportPathRegistry):

    """Metrics registry."""

    def __init__(self):
        """Set. defaults."""
        super(MetricsRegistry, self).__init__(
            initial=cfg.get('QUOTAS_METRICS', []),
            load_modules=True,
        )

    def _load_import_path(self, import_path):
        """ Load module behind an import path """
        m = super(MetricsRegistry, self)._load_import_path(import_path)
        if not issubclass(Metric, m):
            raise RegistryError("{0} is not a subclass of Metric.")


metrics_registry = RegistryProxy('quotas_metrics', MetricsRegistry)
