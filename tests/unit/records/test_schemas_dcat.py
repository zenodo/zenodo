# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

"""Test the DCAT serializer."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.serializers import dcat_v1


def test_dcat_serializer(db, es, record_with_bucket):
    """Tests the DCAT XSLT-based serializer."""
    pid, record = record_with_bucket
    serialized_record = dcat_v1.serialize(pid, record)
    assert record['title'] in serialized_record
    assert record['description'] in serialized_record
    assert record['doi'] in serialized_record
    for creator in record['creators']:
        assert creator['familyname'] in serialized_record
        assert creator['givennames'] in serialized_record
    for f in record['_files']:
        assert f['key'] in serialized_record
