# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests for deposit/record minters."""

from __future__ import absolute_import, print_function

from uuid import uuid4

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from zenodo.modules.deposit.minters import zenodo_deposit_minter
from zenodo.modules.records.minters import zenodo_record_minter


def test_double_minting_depid_recid(db):
    """Test using same integer for dep/rec ids."""
    dep_uuid = uuid4()
    data = dict()
    pid = zenodo_deposit_minter(dep_uuid, data)
    # Assert values added to data
    assert data['_deposit']['id'] == '1'
    assert data['recid'] == 1
    assert 'doi' not in data
    # Assert pid values
    assert pid.pid_type == 'depid'
    assert pid.pid_value == '1'
    assert pid.status == PIDStatus.REGISTERED
    assert pid.object_uuid == dep_uuid
    # Assert reservation of recid.
    assert PersistentIdentifier.get('recid', pid.pid_value).status \
        == PIDStatus.RESERVED
    db.session.commit()

    # Assert registration of recid.
    rec_uuid = uuid4()
    pid = zenodo_record_minter(rec_uuid, data)
    assert pid.pid_type == 'recid'
    assert pid.pid_value == '1'
    assert pid.status == PIDStatus.REGISTERED
    assert pid.object_uuid == rec_uuid
    assert data['doi'] == '10.5072/zenodo.1'


@pytest.mark.parametrize('doi_in, doi_out', [
    # ('10.1234/foo', '10.1234/foo'),
    # ('10.5072/foo', '10.5072/foo'),
    (None, '10.5072/zenodo.1'),
])
def test_doi_minting(db, doi_in, doi_out):
    """Test using same integer for dep/rec ids."""
    dep_uuid, rec_uuid = uuid4(), uuid4()
    data = dict(doi=doi_in)
    zenodo_deposit_minter(dep_uuid, data)
    zenodo_record_minter(rec_uuid, data)
    db.session.commit()

    pid = PersistentIdentifier.get('doi', doi_out)
    assert pid.object_uuid == rec_uuid
    assert pid.status == PIDStatus.RESERVED


@pytest.mark.parametrize('doi', [
    '1234/foo',
    'a',
])
def test_invalid_doi(db, doi):
    """Test using same integer for dep/rec ids."""
    dep_uuid = uuid4()
    data = dict(doi=doi)
    zenodo_deposit_minter(dep_uuid, data)
    assert PersistentIdentifier.query.count() == 2
