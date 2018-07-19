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

"""Statistics events builders."""

from zenodo.modules.records.utils import is_deposit

from .utils import extract_event_record_metadata, get_record_from_context


def skip_deposit(event, sender_app, **kwargs):
    """Check if event is coming from deposit record and skip."""
    record = get_record_from_context(**kwargs)
    if record and is_deposit(record):
        # TODO: Check that invenio-stats bails when `None` is returned
        return None
    return event


def add_record_metadata(event, sender_app, **kwargs):
    """Add Zenodo-specific record fields to the event."""
    record = get_record_from_context(**kwargs)
    if record:
        event.update(extract_event_record_metadata(record))
    return event
