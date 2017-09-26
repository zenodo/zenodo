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

"""Persistent identifier field."""

from __future__ import absolute_import, print_function

import idutils
from flask_babelex import lazy_gettext as _
from marshmallow import missing

from .sanitizedunicode import SanitizedUnicode


class PersistentId(SanitizedUnicode):
    """Special DOI field."""

    default_error_messages = {
        'invalid_scheme': 'Not a valid {scheme} identifier.',
        # TODO: Translation on format strings sounds tricky...
        # 'invalid_scheme': _('Not a valid {scheme} identifier.'),
        'invalid_pid': _('Not a valid persistent identifier.'),
    }

    def __init__(self, scheme=None, normalize=True, *args, **kwargs):
        """Initialize field."""
        super(PersistentId, self).__init__(*args, **kwargs)
        self.scheme = scheme
        self.normalize = normalize

    def _serialize(self, value, attr, obj):
        """Serialize persistent identifier value."""
        if not value:
            return missing
        return value

    def _deserialize(self, value, attr, data):
        """Deserialize persistent identifier value."""
        value = super(PersistentId, self)._deserialize(value, attr, data)
        value = value.strip()

        schemes = idutils.detect_identifier_schemes(value)
        if self.scheme and self.scheme.lower() not in schemes:
            self.fail('invalid_scheme', scheme=self.scheme)
        if not schemes:
            self.fail('invalid_pid')
        return idutils.normalize_pid(value, schemes[0]) \
            if self.normalize else value
