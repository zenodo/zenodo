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

"""Zenodo module that adds support for prometheus metrics."""

from flask import Blueprint, Response, current_app
from . import utils

blueprint = Blueprint(
    'zenodo_metrics',
    __name__
)


@blueprint.route('/metrics/<string:metric_id>')
def metrics(metric_id):
    """Metrics endpoint."""
    if metric_id not in current_app.config['ZENODO_METRICS_DATA']:
        return Response('Invalid key', status=404, mimetype='text/plain')

    metrics = utils.calculate_metrics(metric_id)
    response = utils.formatted_response(metrics)
    return Response(response, mimetype='text/plain')
