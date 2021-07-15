# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017-2021 CERN.
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

"""Utilities for metrics module."""
from flask import current_app
from copy import deepcopy
from invenio_cache import current_cache


def calculate_metrics(metric_id, cache=True):
    if cache:
        cached_data = current_cache.get(
            'ZENODO_METRICS_CACHE::{}'.format(metric_id))
        if cached_data is not None:
            return cached_data

    result = deepcopy(
        current_app.config['ZENODO_METRICS_DATA'][metric_id])

    for metric in result:
        metric['value'] = metric['value']()

    current_cache.set('ZENODO_METRICS_CACHE::{}'.format(metric_id), result,
                      timeout=current_app.config[
                          'ZENODO_METRICS_CACHE_TIMEOUT'])

    return result


def formatted_response(metrics):
    response = ''
    for metric in metrics:
        response += "# HELP {name} {help}\n# TYPE {name} {type}\n{name} " \
                    "{value}\n".format(**metric)

    return response
