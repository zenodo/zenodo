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

"""Statistics utilities."""

from flask import request


def get_record_from_context(**kwargs):
    """Get the cached record object from kwargs or the request context."""
    if 'record' in kwargs:
        return kwargs['record']
    else:
        if request and \
                hasattr(request._get_current_object(), 'current_file_record'):
            return request.current_file_record


def extract_event_record_metadata(record):
    """Extract from a record the payload needed for a statistics event."""
    return dict(
        record_id=str(record.id),
        recid=str(record['recid']) if record.get('recid') else None,
        conceptrecid=record.get('conceptrecid'),
        doi=record.get('doi'),
        conceptdoi=record.get('conceptdoi'),
        access_right=record.get('access_right'),
        resource_type=record.get('resource_type'),
        communities=record.get('communities'),
        owners=record.get('owners'),
    )
