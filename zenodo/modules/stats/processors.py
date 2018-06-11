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

"""Statistics events processors."""

from invenio_records.models import RecordMetadata
from invenio_records_files.models import RecordsBuckets

from zenodo.modules.records.utils import is_deposit


def skip_deposit_file(doc):
    """Check if event is coming from deposit file and skip."""
    rb = RecordsBuckets.query.filter_by(bucket_id=doc["bucket_id"]).first()
    record = RecordMetadata.query.filter_by(id=rb.record_id).first()
    if is_deposit(record.json):
        return None
    return doc


def skip_deposit_record(doc):
    """Check if event is coming from deposit record and skip."""
    return None if doc["pid_type"] == "depid" else doc
