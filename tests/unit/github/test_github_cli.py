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


"""Test CLI for GitHub."""

from __future__ import absolute_import, print_function

import pytest
from invenio_github.api import GitHubAPI


def test_hook_sync(mocker, app, cli_run, g_tester_id):
    """Test 'sync' CLI."""
    # Test with user's email
    mock_obj = mocker.patch.object(GitHubAPI, 'sync')
    ret = cli_run('sync info@inveniosoftware.org -E')
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(hooks=False, async_hooks=False)

    # Test call with user ID
    mock_obj = mocker.patch.object(GitHubAPI, 'sync')
    ret = cli_run('sync {0} -E'.format(g_tester_id))
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(hooks=False, async_hooks=False)

    # Test call with flags
    mock_obj = mocker.patch.object(GitHubAPI, 'sync')
    ret = cli_run('sync info@inveniosoftware.org --hooks True'
                  ' --async-hooks=True -E')
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(hooks=True, async_hooks=True)


def test_hook_create(mocker, app, cli_run, g_users, g_repositories):
    """Test 'createhook' CLI."""
    mock_obj = mocker.patch.object(GitHubAPI, 'create_hook')
    ret = cli_run('createhook u1@foo.bar foo/bar --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output.startswith('Hook is already installed for')
    assert not mock_obj.called

    repo = g_repositories[1]  # baz/spam repository
    mock_obj = mocker.patch.object(GitHubAPI, 'create_hook')
    ret = cli_run('createhook u1@foo.bar baz/spam --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(repo['github_id'], repo['name'])

    mock_obj = mocker.patch.object(GitHubAPI, 'create_hook')
    ret = cli_run('createhook u1@foo.bar {0} --yes-i-know -E'.format(
        repo['github_id']))
    assert ret.output == ''
    assert ret.exit_code == 0
    mock_obj.assert_called_once_with(repo['github_id'], repo['name'])


def test_hook_remove(mocker, app, cli_run, g_users, g_repositories):
    """Test 'removehook' CLI."""
    repo0 = g_repositories[0]  # foo/bar repository, owned by u1
    repo1 = g_repositories[1]  # baz/spam repository, orphaned

    # Remove hook from an 'enabled' repo without a user
    mock_obj = mocker.patch.object(GitHubAPI, 'remove_hook')
    ret = cli_run('removehook foo/bar --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(repo0['github_id'], repo0['name'])

    # Remove hook from an 'enabled' repo with owner specified
    mock_obj = mocker.patch.object(GitHubAPI, 'remove_hook')
    ret = cli_run('removehook foo/bar -u u1@foo.bar --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == ''
    mock_obj.assert_called_once_with(repo0['github_id'], repo0['name'])

    # Remove hook from an 'enabled' repo with non-owner specified
    mock_obj = mocker.patch.object(GitHubAPI, 'remove_hook')
    ret = cli_run('removehook foo/bar -u u2@foo.bar --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == \
        'Warning: Specified user is not the owner of this repository.\n'
    mock_obj.assert_called_once_with(repo0['github_id'], repo0['name'])

    # Remove hook from an orphaned repo without specifying a user
    mock_obj = mocker.patch.object(GitHubAPI, 'remove_hook')
    ret = cli_run('removehook baz/spam --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == \
        "Repository doesn't have an owner, please specify a user.\n"
    assert not mock_obj.called

    # Remove hook from an orphaned repo with user specified
    mock_obj = mocker.patch.object(GitHubAPI, 'remove_hook')
    ret = cli_run('removehook baz/spam -u u1@foo.bar --yes-i-know -E')
    assert ret.exit_code == 0
    assert ret.output == 'Warning: Repository is not owned by any user.\n'
    mock_obj.assert_called_once_with(repo1['github_id'], repo1['name'])


def test_repo_list(app, cli_run, g_users, g_repositories, g_remoteaccounts):
    """Test 'list' CLI."""
    # List repos 'owned' by the user
    ret = cli_run('list u1@foo.bar -E')
    assert ret.exit_code == 0
    assert ret.output.startswith('User has 2 enabled repositories.')
    assert 'foo/bar:8000' in ret.output
    assert 'bacon/eggs:8002' in ret.output
    assert 'other/repo:8003' not in ret.output


def test_repo_assign(mocker, app, cli_run, g_users, g_repositories):
    """Test 'assign' CLI."""
    rh_mock = mocker.patch.object(GitHubAPI, 'remove_hook')
    ch_mock = mocker.patch.object(GitHubAPI, 'create_hook')
    ret = cli_run('assign u2@foo.bar 8000 --yes-i-know -E')
    assert ret.exit_code == 0
    rh_mock.assert_called_once_with(8000, 'foo/bar')
    ch_mock.assert_called_once_with(8000, 'foo/bar')


@pytest.mark.parametrize('u2', ['u2@foo.bar', '2'])
@pytest.mark.parametrize('r1', ['foo/bar', '8000'])
@pytest.mark.parametrize('r2', ['bacon/eggs', '8002'])
def test_repo_assign_many(mocker, r2, r1, u2, app, cli_run,
                          g_users, g_repositories):
    """Test 'assign' CLI."""
    # Make sure the 'u2' parameter is correct
    rh_mock = mocker.patch.object(GitHubAPI, 'remove_hook')
    ch_mock = mocker.patch.object(GitHubAPI, 'create_hook')
    assert g_users[1]['email'] == 'u2@foo.bar'
    assert g_users[1]['id'] == 2
    cmd = 'assign {0} {1} {2} --yes-i-know -E'.format(u2, r1, r2)
    ret = cli_run(cmd)
    assert ret.exit_code == 0
    rh_mock.call_count == 2
    ch_mock.call_count == 2
    rh_mock.assert_any_call(8000, 'foo/bar')
    rh_mock.assert_any_call(8002, 'bacon/eggs')
    ch_mock.assert_any_call(8000, 'foo/bar')
    ch_mock.assert_any_call(8002, 'bacon/eggs')
