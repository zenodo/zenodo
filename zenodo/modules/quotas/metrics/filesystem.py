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

"""Account metrics."""

from __future__ import absolute_import

import os

from flask import current_app

from ..models import Metric


class FilesystemMetric(Metric):

    """Aggregated metrics for filesystem."""

    metric_class = "filesystem"
    object_type = "System"

    @classmethod
    def all(cls):
        """Compute file system properties."""
        tmpshared_files = len(
            os.listdir(current_app.config.get("CFG_TMPSHAREDDIR"))
        )

        system_name = current_app.config.get('CFG_SITE_NAME', 'Invenio')
        data = {system_name: {
            'tmpshared.files': tmpshared_files,
        }}

        return data.items()
