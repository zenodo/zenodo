# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""DoJSON based MARCXML serializer for records."""

from __future__ import absolute_import, print_function

from invenio_marc21.serializers.marcxml import MARCXMLSerializer

from .pidrelations import preprocess_oai_record


class ZenodoMARCXMLSerializer(MARCXMLSerializer):
    """Zenodo MARCXML serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def preprocess_record(self, pid, record, links_factory=None):
        """Add related identifiers from PID relations."""
        result = super(ZenodoMARCXMLSerializer, self).preprocess_record(
            pid, record, links_factory=links_factory
        )
        result = preprocess_oai_record(pid, record, result)
        return result
