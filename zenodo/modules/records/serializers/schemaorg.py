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

"""Zenodo schema.org serializer."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.models import ObjectType
from zenodo.modules.records.serializers.schemas import schemaorg as schemas

from .json import ZenodoJSONSerializer


class ZenodoSchemaOrgSerializer(ZenodoJSONSerializer):
    """Zenodo schema.org serializer.

    Serializes the record using the appropriate marshmallow schema based on
    its schema.org type.
    """

    @classmethod
    def _get_schema_class(self, obj):
        data = obj['metadata']
        obj_type = ObjectType.get_by_dict(data['resource_type'])
        return getattr(schemas, obj_type['schema.org'][19:])

    def dump(self, obj, context=None):
        """Serialize object with schema."""
        # Resolve string "https://schema.org/ScholarlyArticle"
        # to schemas.ScholarlyArticle class (etc.)
        schema_cls = self._get_schema_class(obj)
        return schema_cls(context=context).dump(obj).data
