# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Exporter writers tests."""

from __future__ import absolute_import, print_function

import pytest
from invenio_files_rest.models import ObjectVersion
from six import BytesIO

from zenodo.modules.exporter import filename_factory


def test_filename_factory():
    """Test filename factory."""
    pytest.raises(KeyError, filename_factory())

    fname = filename_factory(name='records', format='json')()
    assert fname.startswith('records-')
    assert fname.endswith('.json')


def test_bucket_writer(writer):
    """Test bucket writer."""
    writer.open()
    assert writer.obj.file_id is None
    writer.write(BytesIO(b'this is a test'))
    writer.close()
    assert ObjectVersion.get(writer.bucket_id, writer.key).file_id is not None
