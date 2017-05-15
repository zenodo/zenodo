# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""PID Version relation schemas."""

from invenio_pidrelations.serializers.schemas import RelationSchema
from marshmallow import fields


class VersionRelation(RelationSchema):
    """PID version relation schema."""

    count = fields.Method('dump_count')

    last_child = fields.Method('dump_last_child')
    draft_child_deposit = fields.Method('dump_draft_child_deposit')

    def dump_count(self, obj):
        """Dump the number of children."""
        # import ipdb; ipdb.set_trace()
        return obj.children.count()

    def dump_last_child(self, obj):
        """Dump the last child."""
        if obj.is_ordered:
            return self._dump_relative(obj.last_child)

    def dump_draft_child_deposit(self, obj):
        """Dump the deposit of the draft child."""
        if obj.draft_child_deposit:
            return self._dump_relative(obj.draft_child_deposit)

    class Meta:
        """Meta fields of the schema."""

        fields = ('parent', 'is_last', 'index', 'last_child', 'count',
                  'draft_child_deposit')
