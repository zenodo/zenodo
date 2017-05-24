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

"""Test API for Zenodo and GitHub integration."""

from __future__ import absolute_import, print_function

from contextlib import contextmanager
from copy import deepcopy

import pytest
from flask import current_app
from invenio_accounts.models import User
from invenio_github.models import Release, ReleaseStatus, Repository
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_sipstore.models import SIP
from mock import MagicMock, Mock, patch
from six import BytesIO

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.github.api import ZenodoGitHubRelease
from zenodo.modules.github.utils import is_github_owner, is_github_versioned
from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.minters import zenodo_record_minter
from zenodo.modules.records.permissions import has_newversion_permission, \
    has_update_permission

creators_params = (
    (dict(),
     [dict(name='Contributor', affiliation='X'), ],
     [dict(name='Owner', affiliation='Y'), ],
     [dict(name='Contributor', affiliation='X'), ]),
    (dict(creators=[]),  # List of creators provided as empty
     [dict(name='Contributor', affiliation='X'), ],
     [dict(name='Owner', affiliation='Y'), ],
     [dict(name='Owner', affiliation='Y'), ]),
    (dict(creators=None),
     [dict(name='Contributor', affiliation='X'), ],
     None,  # Failed to get GH owner
     [dict(name='Unknown', affiliation=''), ]),
)


@pytest.mark.parametrize('defaults,contribs,owner,output', creators_params)
@patch('zenodo.modules.github.api.get_owner')
@patch('zenodo.modules.github.api.get_contributors')
@patch('zenodo.modules.github.api.legacyjson_v1_translator')
def test_github_creators_metadata(m_ljv1t, m_get_contributors, m_get_owner,
                                  defaults, contribs, owner, output):
    """Test 'creators' metadata fetching from GitHub."""
    m_get_contributors.return_value = contribs
    m_get_owner.return_value = owner
    release = MagicMock()
    release.event.user_id = 1
    release.event.payload['repository']['id'] = 1
    zgh = ZenodoGitHubRelease(release)
    zgh.defaults = defaults
    zgh.gh.api = None
    zgh.extra_metadata = {}
    zgh.metadata
    m_ljv1t.assert_called_with({'metadata': {'creators': output}})


@patch('zenodo.modules.github.api.ZenodoGitHubRelease.metadata')
@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_github_publish(datacite_mock, zgh_meta, db, users, location,
                        deposit_metadata):
    """Test basic GitHub payload."""
    data = b'foobar'
    resp = Mock()
    resp.headers = {'Content-Length': len(data)}
    resp.raw = BytesIO(b'foobar')
    resp.status_code = 200
    gh3mock = MagicMock()
    gh3mock.api.session.get = Mock(return_value=resp)
    gh3mock.account.user.email = 'foo@baz.bar'
    release = MagicMock()
    release.event.user_id = 1
    release.event.payload['release']['author']['id'] = 1
    release.event.payload['foo']['bar']['baz'] = 1
    release.event.payload['repository']['id'] = 1

    zgh = ZenodoGitHubRelease(release)
    zgh.gh = gh3mock
    zgh.release = dict(author=dict(id=1))
    zgh.metadata = deposit_metadata
    zgh.files = (('foobar.txt', None), )
    zgh.model.repository.releases.filter_by().count.return_value = 0

    datacite_task_mock = MagicMock()
    # We have to make the call to the task synchronous
    datacite_task_mock.delay = datacite_register.apply
    with patch('zenodo.modules.deposit.tasks.datacite_register',
               new=datacite_task_mock):
        zgh.publish()

    # datacite should be called twice - for regular DOI and Concept DOI
    assert datacite_mock().metadata_post.call_count == 2
    datacite_mock().doi_post.assert_any_call(
        '10.5072/zenodo.1', 'https://zenodo.org/record/1')
    datacite_mock().doi_post.assert_any_call(
        '10.5072/zenodo.2', 'https://zenodo.org/record/2')

    expected_sip_agent = {
        'email': 'foo@baz.bar',
        '$schema': 'http://zenodo.org/schemas/sipstore/'
                   'agent-githubclient-v1.0.0.json',
        'user_id': 1,
        'github_id': 1,
    }
    gh_sip = SIP.query.one()
    assert gh_sip.agent == expected_sip_agent


@patch('invenio_github.api.GitHubAPI.check_sync', new=lambda *_, **__: False)
def test_github_newversion_permissions(app, db, minimal_record, users, g_users,
                                       g_remoteaccounts):
    """Test new version creation permissions for GitHub records."""

    old_owner, new_owner = [User.query.get(u['id']) for u in g_users]

    # Create repository, and set owner to `old_owner`
    repo = Repository.create(
        name='foo/bar', github_id=8000, user_id=old_owner.id, hook=1234)

    # Create concpetrecid for the GitHub records
    conceptrecid = PersistentIdentifier.create(
        'recid', '100', status=PIDStatus.RESERVED)

    def create_deposit_and_record(pid_value, owner):
        """Utility function for creating records and deposits."""
        recid = PersistentIdentifier.create(
            'recid', pid_value, status=PIDStatus.RESERVED)
        pv = PIDVersioning(parent=conceptrecid)
        pv.insert_draft_child(recid)

        depid = PersistentIdentifier.create(
            'depid', pid_value, status=PIDStatus.REGISTERED)
        deposit = ZenodoRecord.create({'_deposit': {'id': depid.pid_value},
                                       'conceptrecid': conceptrecid.pid_value,
                                       'recid': recid.pid_value})
        deposit.commit()
        depid.assign('rec', deposit.id)

        record_metadata = deepcopy(minimal_record)
        record_metadata['_deposit'] = {'id': depid.pid_value}
        record_metadata['conceptrecid'] = conceptrecid.pid_value
        record_metadata['recid'] = int(recid.pid_value)
        record_metadata['owners'] = [owner.id]
        record = ZenodoRecord.create(record_metadata)
        zenodo_record_minter(record.id, record)
        record.commit()

        return (depid, deposit, recid, record)

    # Create first GitHub record (by `old_owner`)
    depid1, d1, recid1, r1 = create_deposit_and_record('101', old_owner)
    rel1 = Release(release_id=111, repository_id=repo.id, record_id=d1.id,
                   status=ReleaseStatus.PUBLISHED)
    db.session.add(rel1)
    db.session.commit()

    assert is_github_versioned(recid1)

    @contextmanager
    def set_identity(user):
        from flask_principal import AnonymousIdentity, Identity
        principal = current_app.extensions['security'].principal
        principal.set_identity(Identity(user))
        yield
        principal.set_identity(AnonymousIdentity())

    with app.test_request_context():
        with set_identity(old_owner):
            assert is_github_owner(old_owner, recid1)
            assert has_update_permission(old_owner, r1)
            assert has_newversion_permission(old_owner, r1)

        with set_identity(new_owner):
            assert not is_github_owner(new_owner, recid1)
            assert not has_update_permission(new_owner, r1)
            assert not has_newversion_permission(new_owner, r1)

    # Change the repository owner
    repo.user_id = new_owner.id
    db.session.add(repo)
    db.session.commit()

    with app.test_request_context():
        with set_identity(old_owner):
            assert not is_github_owner(old_owner, recid1)
            # `old_owner` can edit his record of course
            assert has_update_permission(old_owner, r1)
            assert has_newversion_permission(old_owner, r1)

        with set_identity(new_owner):
            assert is_github_owner(new_owner, recid1)
            # `new_owner` can't edit the `old_owner`'s record
            assert not has_update_permission(new_owner, r1)
            assert not has_newversion_permission(new_owner, r1)

    # Create second GitHub record (by `new_owner`)
    depid2, d2, recid2, r2 = create_deposit_and_record('102', new_owner)
    rel2 = Release(release_id=222, repository_id=repo.id, record_id=d2.id,
                   status=ReleaseStatus.PUBLISHED)
    db.session.add(rel2)
    db.session.commit()

    with app.test_request_context():
        with set_identity(old_owner):
            assert not is_github_owner(old_owner, recid1)
            assert not is_github_owner(old_owner, recid2)
            assert has_update_permission(old_owner, r1)
            # `old_owner` can't edit the `new_owner`'s record
            assert not has_update_permission(old_owner, r2)
            assert not has_newversion_permission(old_owner, r1)
            assert not has_newversion_permission(old_owner, r2)

        with set_identity(new_owner):
            assert is_github_owner(new_owner, recid1)
            assert is_github_owner(new_owner, recid2)
            assert not has_update_permission(new_owner, r1)
            # `new_owner` can edit his newly released record
            assert has_update_permission(new_owner, r2)
            assert has_newversion_permission(new_owner, r1)
            assert has_newversion_permission(new_owner, r2)

    # Create a manual record (by `new_owner`)
    depid3, d3, recid3, r3 = create_deposit_and_record('103', new_owner)
    db.session.commit()

    with app.test_request_context():
        with set_identity(old_owner):
            assert not is_github_owner(old_owner, recid3)
            assert not has_update_permission(old_owner, r3)
            assert not has_newversion_permission(old_owner, r3)

        with set_identity(new_owner):
            assert is_github_owner(new_owner, recid3)
            assert has_update_permission(new_owner, r3)
            assert has_newversion_permission(new_owner, r3)
