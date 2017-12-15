# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Zenodo schema.org marshmallow schema."""

from __future__ import absolute_import, print_function, unicode_literals

import idutils
from flask import current_app
from marshmallow import Schema, fields, missing

from ...models import ObjectType
from ..fields import SanitizedHTML, SanitizedUnicode
from .common import format_pid_link


class CreativeWorkV1(Schema):
    """Schema for schema.org/CreativeWork type."""

    CONTEXT = "https://schema.org/"

    doi = fields.Method('get_doi', dump_to='@id')
    type_ = fields.Method('get_type', dump_to='@type')
    name = SanitizedUnicode(attribute='metadata.title')
    description = SanitizedHTML(attribute='metadata.description')
    context = fields.Method('get_context', dump_to='@context')
    #keywords = fields.List(attribute='metadata.keywords')

    url = fields.Method('get_url')

    def get_context(self, obj):
        """Returns the value for '@context' value."""
        return self.CONTEXT

    def get_doi(self, obj):
        """Get DOI of the record."""
        data = obj['metadata']
        return idutils.to_url(data['doi'], 'doi') if data['doi'] else missing

    def get_type(self, obj):
        """Get schema.org type of the record."""
        data = obj['metadata']
        obj_type = ObjectType.get_by_dict(data['resource_type'])
        return (obj_type['schema.org'][len(self.CONTEXT):]
                if obj_type else missing)

    def get_url(self, obj):
        """Get Zenodo URL of the record."""
        recid = obj.get('recid')
        return format_pid_link(
            current_app.config['RECORDS_UI_ENDPOINT'], recid
        ) if recid else missing
