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

"""Configuration for quota module."""


QUOTAS_METRICS = [
    'zenodo.modules.quotas.metrics.afs:AFSVolumeMetric',
    'zenodo.modules.quotas.metrics.deposit:DepositMetric',
]

QUOTAS_PUBLISH_METRICS = []
"""Determine which metrics to publish."""

QUOTAS_AFSMETRIC_DIRECTORIES = [
    "var/data/deposit/",
    "var/data/files/",
]
"""AFS directories for AFS metric."""

#
# XSLS related variables.
#

QUOTAS_XSLS_API_URL = "http://xsls-dev.cern.ch"
"""XSLS API endpoint."""

QUOTAS_XSLS_SERVICE_ID = None
"""XSLS service id."""

QUOTAS_XSLS_AVAILABILITY = 'zenodo.base.metrics.availability'
"""Import path to callable that will compute an availability value (0-100).

The callable must take one argument which is the ServiceDocument that will
be sent to the XSLS service.

See http://itmon.web.cern.ch/itmon/recipes/how_to_create_a_service_xml.html
"""
