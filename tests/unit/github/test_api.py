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

import pytest
from invenio_sipstore.models import SIP
from mock import MagicMock, Mock, patch
from six import BytesIO

from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.github.api import ZenodoGitHubRelease

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
