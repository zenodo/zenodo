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
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from zenodo.modules.deposit.minters import zenodo_deposit_minter
from zenodo.modules.records.minters import zenodo_record_minter


def test_double_minting_depid_recid(db):
    """Test using same integer for dep/rec ids."""
    dep_uuid = uuid4()
    data = dict()
    pid = zenodo_deposit_minter(dep_uuid, data)
    # Assert values added to data. Depid and recid have IDs starting from
    # '2' since the conceptrecid is minted first
    assert data['_deposit']['id'] == '2'
    assert data['conceptrecid'] == '1'
    assert data['recid'] == 2
    assert 'doi' not in data
    # Assert pid values
    assert pid.pid_type == 'depid'
    assert pid.pid_value == '2'
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
    assert pid.pid_value == '2'
    assert pid.status == PIDStatus.REGISTERED
    assert pid.object_uuid == rec_uuid
    assert data['doi'] == '10.5072/zenodo.2'
    assert data['_oai']['id'] == 'oai:zenodo.org:2'


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
    assert PersistentIdentifier.query.count() == 3


def test_unpublished_deposit_and_pid_deletion(deposit):
    """Test deletion of deposit and pid."""
    recid = PersistentIdentifier.get('recid', str(deposit['recid']))
    assert recid and recid.status == PIDStatus.RESERVED
    assert not recid.has_object()
    depid = PersistentIdentifier.get('depid', str(deposit['_deposit']['id']))
    assert depid and depid.status == PIDStatus.REGISTERED
    assert depid.has_object()

    # Delete deposit
    deposit.delete()

    pytest.raises(
        PIDDoesNotExistError,
        PersistentIdentifier.get,
        'recid', str(deposit['recid'])
    )
    depid = PersistentIdentifier.get('depid', str(deposit['_deposit']['id']))
    assert depid and depid.status == PIDStatus.DELETED


def test_published_external_doi(db, deposit, deposit_file):
    """Test published external DOI."""
    ext_doi1 = '10.1234/foo'
    ext_doi2 = '10.1234/bar'
    deposit['doi'] = ext_doi1
    deposit.publish()
    db.session.commit()

    # Published record with external DOI must have:
    # 1) a registered recid with object
    recid = PersistentIdentifier.get('recid', str(deposit['recid']))
    assert recid and recid.status == PIDStatus.REGISTERED \
        and recid.has_object()
    # 2) a reserved external doi with object
    doi = PersistentIdentifier.get('doi', ext_doi1)
    assert doi and doi.status == PIDStatus.RESERVED \
        and doi.has_object()

    # Now change external DOI.
    deposit = deposit.edit()
    deposit['doi'] = ext_doi2
    deposit.publish()
    db.session.commit()

    # Ensure DOI 1 has been removed.
    pytest.raises(
        PIDDoesNotExistError, PersistentIdentifier.get, 'doi', ext_doi1)

    # Ensure DOI 2 has been reserved.
    doi = PersistentIdentifier.get('doi', ext_doi2)
    assert doi and doi.status == PIDStatus.RESERVED \
        and doi.has_object()
