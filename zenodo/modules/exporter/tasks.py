# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Celery tasks for export jobs."""

from __future__ import absolute_import, print_function

from celery import shared_task
from flask import current_app

from .api import Exporter


@shared_task
def export_job(job_id=None):
    """Export job."""
    base_url = current_app.config['THEME_SITEURL']
    # Execute in API request context, to enable proper URL generation.
    with current_app.test_request_context(base_url):
        job_definition = current_app.extensions['invenio-exporter'].job(job_id)
        Exporter(**job_definition).run()
