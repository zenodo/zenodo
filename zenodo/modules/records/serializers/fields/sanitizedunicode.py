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

"""Sanitized Unicode string field."""

from __future__ import absolute_import, print_function

from ftfy import fix_text

from .trimmedstring import TrimmedString


class SanitizedUnicode(TrimmedString):
    """String field that sanitizes and fixes problematic unicode characters."""

    UNWANTED_CHARACTERS = {
        # Zero-width space
        u'\u200b',
    }

    def is_valid_xml_char(self, char):
        """Check if a character is valid based on the XML specification."""
        codepoint = ord(char)
        return (0x20 <= codepoint <= 0xD7FF or
                codepoint in (0x9, 0xA, 0xD) or
                0xE000 <= codepoint <= 0xFFFD or
                0x10000 <= codepoint <= 0x10FFFF)

    def _deserialize(self, value, attr, data):
        """Deserialize sanitized string value."""
        value = super(SanitizedUnicode, self)._deserialize(value, attr, data)
        value = fix_text(value)

        # NOTE: This `join` might be inefficient... There's a solution with a
        # large compiled regex lying around, but needs a lot of tweaking.
        value = ''.join(filter(self.is_valid_xml_char, value))
        for char in self.UNWANTED_CHARACTERS:
            value = value.replace(char, '')
        return value
