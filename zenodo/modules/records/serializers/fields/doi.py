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

"""DOI field."""

from __future__ import absolute_import, print_function

import idutils
from flask_babelex import lazy_gettext as _
from marshmallow import fields


class DOI(fields.String):
    """Special DOI field."""

    default_error_messages = {
        'invalid_doi': _(
            'The provided DOI is invalid - it should look similar '
            ' to \'10.1234/foo.bar\'.'),
        'invalid_prefix': _(
            'The prefix {prefix} is administrated locally.'),
        'banned_prefix': _(
            'The prefix {prefix} is invalid.'
        ),
        'test_prefix': _(
            'The prefix {prefix} is invalid. The '
            'prefix is only used for testing purposes, and no DOIs with '
            'this prefix are attached to any meaningful content.'
        ),
    }

    def __init__(self, allowed_prefixes=None, banned_prefixes=None,
                 *args, **kwargs):
        """Initialize field."""
        super(DOI, self).__init__(*args, **kwargs)
        self.allowed_prefixes = allowed_prefixes or []
        self.banned_prefixes = banned_prefixes or ['10.5072']

    def _deserialize(self, value, attr, data):
        """Deserialize DOI value."""
        value = super(DOI, self)._deserialize(value, attr, data)
        value = value.strip()
        if not idutils.is_doi(value):
            self.fail('invalid_doi')
        return idutils.normalize_doi(value)

    def _validate(self, value):
        """Validate DOI value."""
        super(DOI, self)._validate(value)

        allowed_prefixes = self.context.get(
            'allowed_prefixes', self.allowed_prefixes)
        banned_prefixes = self.context.get(
            'banned_prefixes', self.banned_prefixes)

        prefix = value.split('/')[0]

        if allowed_prefixes:
            if prefix not in allowed_prefixes:
                self.fail('invalid_prefix', prefix=prefix)
        elif banned_prefixes:
            if prefix in banned_prefixes:
                self.fail(
                    'test_prefix' if prefix == '10.5072' else 'banned_prefix',
                    prefix=prefix
                )
