# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016, 2017 CERN.
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

"""CLI for Zenodo fixtures."""

from __future__ import absolute_import, print_function

from invenio_db import db
from invenio_migrator.tasks.records import import_record
from invenio_sipstore.models import SIPMetadataType


def loaddemorecords(records):
    """Load demo records."""
    for item in records:
        import_record.delay(item, source_type='json'),


def loadsipmetadatatypes(types):
    """Load SIP metadata types."""
    with db.session.begin_nested():
        for type in types:
            db.session.add(SIPMetadataType(**type))
    db.session.commit()
