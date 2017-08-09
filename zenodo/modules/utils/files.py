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

"""Files utilities."""

from __future__ import absolute_import, print_function

import sqlalchemy as sa
from flask import current_app
from invenio_files_rest.models import FileInstance


def checksum_verification_files_query():
    """Return a FileInstance query taking into account file URI prefixes."""
    files = FileInstance.query
    uri_prefixes = current_app.config.get(
        'FILES_REST_CHECKSUM_VERIFICATION_URI_PREFIXES')
    if uri_prefixes:
        files = files.filter(
            sa.or_(*[FileInstance.uri.startswith(p) for p in uri_prefixes]))
    return files
