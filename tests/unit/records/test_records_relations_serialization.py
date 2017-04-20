# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo communities API."""

from __future__ import absolute_import, print_function

from helpers import publish_and_expunge
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.records.serializers.pidrelations import \
    serialize_related_identifiers


def test_serialization(app, db, deposit, deposit_file):
    """Test basic workflow using Deposit and Communities API."""
    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']

    recid_v1, record_v1 = deposit_v1.fetch_published()

    deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    deposit_v2 = deposit_v2.edit()
    # 1. Request for 'c1' and 'c2' through deposit v2
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    recid_v1, record_v1 = deposit_v1.fetch_published()

    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)

    rids = serialize_related_identifiers(recid_v1)
    expected_v1 = [
        {
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.1',
            'relation': 'isPartOf'
        },
        {
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.3',
            'relation': 'isPreviousVersionOf'
        }
    ]
    assert rids == expected_v1

    rids = serialize_related_identifiers(recid_v2)
    expected_v2 = [
        {
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.1',
            'relation': 'isPartOf'
        },
        {
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.2',
            'relation': 'isNewVersionOf'
        }
    ]
    assert rids == expected_v2
    parent_pid = PersistentIdentifier.get('recid', '1')
    rids = serialize_related_identifiers(parent_pid)

    expected_parent = [
        {
            'relation': 'hasPart',
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.2'
        },
        {
            'relation': 'hasPart',
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.3'
        }
    ]
    assert rids == expected_parent
