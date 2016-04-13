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

"""Validators for deposit."""

from __future__ import absolute_import, print_function

from cerberus import Validator as CerberusValidator


def validator(schema, allow_empty=True):
    """Create a validator for schema."""
    def validate(data):
        v = Validator()

        # Either conform to schema or data is empty
        if allow_empty and not data:
            return
        if not v.validate(data, schema):
            raise ValueError(iter_errors(v.errors))

    return validate


def iter_errors(errors):
    """Extract error messages from Cerberus error dictionary."""
    for field, msgs in errors.items():
        if isinstance(msgs, dict):
            for f, m in msgs.items():
                yield dict(
                    field=f,
                    message=m,
                    code=10,
                )
        else:
            yield dict(
                field=field,
                message=msgs,
                code=10,
            )


class Validator(CerberusValidator):
    """Add new datatype 'any', that accepts anything."""

    def _validate_type_any(self, field, value):
        pass
