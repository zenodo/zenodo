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
from invenio_pidrelations.serializers.utils import serialize_relations
from invenio_pidstore.models import PersistentIdentifier
from six import BytesIO, b

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.records.serializers.pidrelations import \
    serialize_related_identifiers


def test_relations_serialization(app, db, deposit, deposit_file):
    """Serialize PID relations."""
    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)

    recid_v1, record_v1 = deposit_v1.fetch_published()
    expected = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 0,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "2"
                },
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
                "count": 1
            }
        ]
    }
    assert serialize_relations(recid_v1) == expected

    deposit_v1.newversion()
    # Should contain "draft_child_deposit" information
    expected = {
        "version": [
            {
                "draft_child_deposit": {
                    "pid_type": "depid",
                    "pid_value": "3"
                },
                "index": 0,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "2"
                },
                "count": 1,
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }
    assert serialize_relations(recid_v1) == expected

    # Publish the new version
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    recid_v2, record_v2 = deposit_v2.fetch_published()
    depid_v1, deposit_v1 = deposit_resolver.resolve(depid_v1_value)
    recid_v1, record_v1 = deposit_v1.fetch_published()

    # Should no longer contain "draft_child_deposit" info after publishing
    # and no longer be the last child
    expected = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 0,
                "is_last": False,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
                "count": 2
            }
        ]
    }
    assert serialize_relations(recid_v1) == expected

    # New version should be the last child now
    expected = {
        "version": [
            {
                "draft_child_deposit": None,
                "index": 1,
                "is_last": True,
                "last_child": {
                    "pid_type": "recid",
                    "pid_value": "3"
                },
                "count": 2,
                "parent": {
                    "pid_type": "recid",
                    "pid_value": "1"
                },
            }
        ]
    }
    assert serialize_relations(recid_v2) == expected


def test_related_identifiers_serialization(app, db, deposit, deposit_file):
    """Serialize PID Relations to related identifiers."""
    deposit_v1 = publish_and_expunge(db, deposit)
    depid_v1_value = deposit_v1['_deposit']['id']

    recid_v1, record_v1 = deposit_v1.fetch_published()

    deposit_v1.newversion()
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.get_assigned_object())
    deposit_v2.files['file.txt'] = BytesIO(b('file1'))
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
            'relation': 'isVersionOf'
        }
        # TODO: serialization of new version realtions is disabled
        # {
        #     'scheme': 'doi',
        #     'identifier': '10.5072/zenodo.3',
        #     'relation': 'isPreviousVersionOf'
        # }
    ]
    assert rids == expected_v1

    rids = serialize_related_identifiers(recid_v2)
    expected_v2 = [
        {
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.1',
            'relation': 'isVersionOf'
        }
        # TODO: serialization of new version realtions is disabled
        # {
        #     'scheme': 'doi',
        #     'identifier': '10.5072/zenodo.2',
        #     'relation': 'isNewVersionOf'
        # }
    ]
    assert rids == expected_v2
    parent_pid = PersistentIdentifier.get('recid', '1')
    rids = serialize_related_identifiers(parent_pid)

    expected_parent = [
        {
            'relation': 'hasVersion',
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.2'
        },
        {
            'relation': 'hasVersion',
            'scheme': 'doi',
            'identifier': '10.5072/zenodo.3'
        }
    ]
    assert rids == expected_parent
