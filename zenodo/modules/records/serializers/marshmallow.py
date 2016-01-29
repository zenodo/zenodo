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

"""Base class for Marshmallow based serializers."""

from __future__ import absolute_import, print_function

from .base import PreprocessorMixin


class MarshmallowSerializer(PreprocessorMixin):
    """Base class for marshmallow serializers."""

    def __init__(self, schema_class):
        """Initialize record."""
        self.schema_class = schema_class

    def dump(self, obj):
        """Serialize object with schema."""
        return self.schema_class().dump(obj).data

    def transform_record(self, pid, record):
        """Transform record into an intermediate representation."""
        return self.dump(self.preprocess_record(pid, record))

    def transform_search_hit(self, pid, record_hit):
        """Transform search result hit into an intermediate representation."""
        return self.dump(self.preprocess_search_hit(pid, record_hit))
