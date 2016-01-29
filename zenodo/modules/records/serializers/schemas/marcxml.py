# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""MARCXML translation index."""

from __future__ import absolute_import, print_function

from dateutil.parser import parse
from marshmallow import Schema, fields


class RecordSchemaMARC(Schema):
    """Schema for records in MARC."""

    control_number = fields.Str(attribute='pid.pid_value')
    date_and_time_of_latest_transaction = fields.Function(
        lambda obj: parse(obj['updated']).strftime("%Y%m%d%H%M%S.0"))
    # title_statement = fields.Function(
    #     lambda obj: dict(title=obj['metadata']['title']))
