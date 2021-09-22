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

"""HTML sanitized string field."""

from __future__ import absolute_import, print_function

import bleach

from .sanitizedunicode import SanitizedUnicode
ALLOWED_TAGS = [
            'a',
            'abbr',
            'acronym',
            'b',
            'blockquote',
            'br',
            'code',
            'caption',
            'div',
            'em',
            'i',
            'li',
            'ol',
            'p',
            'pre',
            'span',
            'strike',
            'strong',
            'sub',
            'sup',
            'table',
            'tbody',
            'thead',
            'th',
            'td',
            'tr',
            'u',
            'ul',
        ]

ALLOWED_ATTRS = {
            '*': ['class'],
            'a': ['href', 'title', 'name', 'rel'],
            'table': ['title',  'align', 'summary'],
            'caption': ['class'],
            'thead': ['title', 'align'],
            'tbody': ['title', 'align'],
            'th': ['title', 'scope'],
            'td': ['title'],
            'tr': ['title'],
            'abbr': ['title'],
            'acronym': ['title'],
        }


class SanitizedHTML(SanitizedUnicode):
    """String field which strips sanitizes HTML using the bleach library."""

    def __init__(self, tags=None, attrs=None, *args, **kwargs):
        """Initialize field."""
        super(SanitizedHTML, self).__init__(*args, **kwargs)
        self.tags = tags or ALLOWED_TAGS
        self.attrs = attrs or ALLOWED_ATTRS

    def _deserialize(self, value, attr, data):
        """Deserialize string by sanitizing HTML."""
        value = super(SanitizedHTML, self)._deserialize(value, attr, data)
        return bleach.clean(
            value,
            tags=self.tags,
            attributes=self.attrs,
            strip=True,
        ).strip()
