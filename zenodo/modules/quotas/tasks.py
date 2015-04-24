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

from werkzeug.utils import import_string

from invenio.celery import celery

from .models import ResourceUsage, Metric


@celery.task(ignore_result=True)
def collect_metric(metric_import_path):
    """Collect a specific metric.

    Use by adding this task to your CELERYBEAT_SCHEDULE

    .. code-block:: python
       CELERYBEAT_SCHEDULE = {
            # Every 15 minutes
            'metrics-afs': dict(
                task='zenodo.modules.quotas.tasks.collect_metric',
                schedule=crontab(minute='*/15'),
                args=('zenodo.modules.quotas.metrics.afs:AFSVolumeMetric', ),
            ),
            # ...
        }


    """
    metric_class = import_string(metric_import_path)

    if not issubclass(metric_class, Metric):
        raise Exception("Invalid metric class: {0}".format(metric_import_path))

    for obj_id, data in metric_class.all():
        for name, val in data.items():
            ResourceUsage.update_or_create(
                metric_class.object_type,
                obj_id,
                metric_class.get_id(name),
                val,
            )
