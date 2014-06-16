# -*- coding: utf-8 -*-
##
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


import json
import httpretty
from six.moves import urllib_parse


def register_github_api():
    register_oauth_flow()
    register_endpoint(
        "/user",
        USER('auser', email='auser@invenio-software.org')
    )
    register_endpoint(
        "/user/orgs",
        [ORG('inveniosoftware'), ],
    )
    register_endpoint(
        "/users/auser/repos",
        [REPO('auser', 'repo-1'), REPO('auser', 'repo-2')]
    )
    register_endpoint(
        "/users/inveniosoftware/repos",
        [REPO('inveniosoftware', 'myorgrepo'), ]
    )
    register_endpoint(
        "/repos/auser/repo-1/contents/.zenodo.json",
        dict(
            message='Not Found',
        ),
        status=404,
    )
    register_endpoint(
        "/repos/auser/repo-1",
        REPO('auser', 'repo-1'),
    )
    register_endpoint(
        "/repos/auser/repo-1/contributors",
        [
            dict(
                contributions=4,
                url='https://api.github.com/users/buser',
                type='User',
            ),
            dict(
                contributions=10,
                url='https://api.github.com/users/auser',
                type='User',
            ),
            dict(
                contributions=1,
                url='https://api.github.com/users/cuser',
                type='User',
            )
        ],
    )
    register_endpoint(
        "/users/auser",
        USER('auser', email='auser@invenio-software.org')
    )
    register_endpoint(
        "/users/buser",
        USER('buser', bio=False)
    )
    register_endpoint(
        "/users/cuser",
        USER('cuser', email='cuser@invenio-software.org')
    )
    httpretty.register_uri(
        httpretty.GET,
        "https://api.github.com/repos/auser/repo-1/zipball/v1.0",
        body=ZIPBALL(stream=True),
        streaming=True,
    )


def register_oauth_flow():
    """ Register URIs used for OAuth flow. """

    # https://developer.github.com/v3/oauth/
    httpretty.register_uri(
        httpretty.GET,
        "https://github.com/login/oauth/authorize",
        status=200,
        body="User required to accept/reject scopes on this page"
    )

    def access_token_callback(request, uri, headers):
        assert request.method == 'POST'
        assert 'client_id' in request.parsed_body
        assert 'client_secret' in request.parsed_body
        assert 'code' in request.parsed_body
        assert 'redirect_uri' in request.parsed_body

        if request.parsed_body['code'][0] == 'bad_verification_code':
            body = dict(
                error_uri='http://developer.github.com/v3/oauth/'
                          '#bad-verification-code',
                error_description='The code passed is '
                                  'incorrect or expired.',
                error='bad_verification_code',
            )
        else:
            body = dict(
                access_token='%s_token' % request.parsed_body['code'][0],
                scope='admin:repo_hook,user:email',
                token_type='bearer',
            )

        headers['content-type'] = 'application/x-www-form-urlencoded'

        return (
            200,
            headers,
            urllib_parse.urlencode(body)
        )

    httpretty.register_uri(
        httpretty.POST,
        "https://github.com/login/oauth/access_token",
        body=access_token_callback,
    )


def register_endpoint(endpoint, body, status=200, method=httpretty.GET):
    """ Mock GitHub API response. """
    httpretty.register_uri(
        method,
        "https://api.github.com%s" % endpoint,
        body=json.dumps(body),
        status=status,
    )


def register_local_endpoint(endpoint, body, status=200, method=httpretty.GET):
    """ Mock GitHub API response. """
    httpretty.register_uri(
        method,
        "https://api.github.com%s" % endpoint,
        body=json.dumps(body),
        status=status,
    )


#
# Fixture generators
#
def USER(login, email=None, bio=True):
    l = login

    user = {
        'avatar_url': 'https://avatars.githubusercontent.com/u/7533764?',
        'collaborators': 0,
        'created_at': '2014-05-09T12:26:44Z',
        'disk_usage': 0,
        'events_url': 'https://api.github.com/users/%s/events{/privacy}' % l,
        'followers': 0,
        'followers_url': 'https://api.github.com/users/%s/followers' % l,
        'following': 0,
        'following_url': 'https://api.github.com/users/%s/following{/other_user}' % l,
        'gists_url': 'https://api.github.com/users/%s/gists{/gist_id}' % l,
        'gravatar_id': '12345678',
        'html_url': 'https://github.com/%s' % l,
        'id': 1234,
        'login': '%s' % l,
        'organizations_url': 'https://api.github.com/users/%s/orgs' % l,
        'owned_private_repos': 0,
        'plan': {
            'collaborators': 0,
            'name': 'free',
            'private_repos': 0,
            'space': 307200},
        'private_gists': 0,
        'public_gists': 0,
        'public_repos': 0,
        'received_events_url': 'https://api.github.com/users/%s/received_events' % l,
        'repos_url': 'https://api.github.com/users/%s/repos' % l,
        'site_admin': False,
        'starred_url': 'https://api.github.com/users/%s/starred{/owner}{/repo}' % l,
        'subscriptions_url': 'https://api.github.com/users/%s/subscriptions' % l,
        'total_private_repos': 0,
        'type': 'User',
        'updated_at': '2014-05-09T12:26:44Z',
        'url': 'https://api.github.com/users/%s' % l,
    }

    if bio:
        user.update({
            'bio': 'Software Engineer at CERN',
            'blog': 'http://www.cern.ch',
            'company': 'CERN',
            'name': 'Lars Holm Nielsen',
        })

    if email is not None:
        user.update({
            'email': email,
        })

    return user


def REPO(owner, repo):
    r = "%s/%s" % (owner, repo)
    o = owner

    return {
        'archive_url': 'https://api.github.com/repos/%s/{archive_format}{/ref}' % r,
        'assignees_url': 'https://api.github.com/repos/%s/assignees{/user}' % r,
        'blobs_url': 'https://api.github.com/repos/%s/git/blobs{/sha}' % r,
        'branches_url': 'https://api.github.com/repos/%s/branches{/branch}' % r,
        'clone_url': 'https://github.com/%s.git' % r,
        'collaborators_url': 'https://api.github.com/repos/%s/collaborators{/collaborator}' % r,
        'comments_url': 'https://api.github.com/repos/%s/comments{/number}' % r,
        'commits_url': 'https://api.github.com/repos/%s/commits{/sha}' % r,
        'compare_url': 'https://api.github.com/repos/%s/compare/{base}...{head}' % r,
        'contents_url': 'https://api.github.com/repos/%s/contents/{+path}' % r,
        'contributors_url': 'https://api.github.com/repos/%s/contributors' % r,
        'created_at': '2012-10-29T10:24:02Z',
        'default_branch': 'master',
        'description': '',
        'downloads_url': 'https://api.github.com/repos/%s/downloads' % r,
        'events_url': 'https://api.github.com/repos/%s/events' % r,
        'fork': False,
        'forks': 0,
        'forks_count': 0,
        'forks_url': 'https://api.github.com/repos/%s/forks' % r,
        'full_name': r,
        'git_commits_url': 'https://api.github.com/repos/%s/git/commits{/sha}' % r,
        'git_refs_url': 'https://api.github.com/repos/%s/git/refs{/sha}' % r,
        'git_tags_url': 'https://api.github.com/repos/%s/git/tags{/sha}' % r,
        'git_url': 'git://github.com/%s.git' % r,
        'has_downloads': True,
        'has_issues': True,
        'has_wiki': True,
        'homepage': None,
        'hooks_url': 'https://api.github.com/repos/%s/hooks' % r,
        'html_url': 'https://github.com/%s' % r,
        'id': 6438791,
        'issue_comment_url': 'https://api.github.com/repos/%s/issues/comments/{number}' % r,
        'issue_events_url': 'https://api.github.com/repos/%s/issues/events{/number}' % r,
        'issues_url': 'https://api.github.com/repos/%s/issues{/number}' % r,
        'keys_url': 'https://api.github.com/repos/%s/keys{/key_id}' % r,
        'labels_url': 'https://api.github.com/repos/%s/labels{/name}' % r,
        'language': None,
        'languages_url': 'https://api.github.com/repos/%s/languages' % r,
        'merges_url': 'https://api.github.com/repos/%s/merges' % r,
        'milestones_url': 'https://api.github.com/repos/%s/milestones{/number}' % r,
        'mirror_url': None,
        'name': 'altantis-conf',
        'notifications_url': 'https://api.github.com/repos/%s/notifications{?since,all,participating}',
        'open_issues': 0,
        'open_issues_count': 0,
        'owner': {
            'avatar_url': 'https://avatars.githubusercontent.com/u/1234?',
            'events_url': 'https://api.github.com/users/%s/events{/privacy}' % o,
            'followers_url': 'https://api.github.com/users/%s/followers' % o,
            'following_url': 'https://api.github.com/users/%s/following{/other_user}' % o,
            'gists_url': 'https://api.github.com/users/%s/gists{/gist_id}' % o,
            'gravatar_id': '1234',
            'html_url': 'https://github.com/%s' % o,
            'id': 1698163,
            'login': '%s' % o,
            'organizations_url': 'https://api.github.com/users/%s/orgs' % o,
            'received_events_url': 'https://api.github.com/users/%s/received_events' % o,
            'repos_url': 'https://api.github.com/users/%s/repos' % o,
            'site_admin': False,
            'starred_url': 'https://api.github.com/users/%s/starred{/owner}{/repo}' % o,
            'subscriptions_url': 'https://api.github.com/users/%s/subscriptions' % o,
            'type': 'User',
            'url': 'https://api.github.com/users/%s' % o
        },
        'permissions': {'admin': True, 'pull': True, 'push': True},
        'private': False,
        'pulls_url': 'https://api.github.com/repos/%s/pulls{/number}' % r,
        'pushed_at': '2012-10-29T10:28:08Z',
        'releases_url': 'https://api.github.com/repos/%s/releases{/id}' % r,
        'size': 104,
        'ssh_url': 'git@github.com:%s.git' % r,
        'stargazers_count': 0,
        'stargazers_url': 'https://api.github.com/repos/%s/stargazers' % r,
        'statuses_url': 'https://api.github.com/repos/%s/statuses/{sha}' % r,
        'subscribers_url': 'https://api.github.com/repos/%s/subscribers' % r,
        'subscription_url': 'https://api.github.com/repos/%s/subscription' % r,
        'svn_url': 'https://github.com/%s' % r,
        'tags_url': 'https://api.github.com/repos/%s/tags' % r,
        'teams_url': 'https://api.github.com/repos/%s/teams' % r,
        'trees_url': 'https://api.github.com/repos/%s/git/trees{/sha}' % r,
        'updated_at': '2013-10-25T11:30:04Z',
        'url': 'https://api.github.com/repos/%s' % r,
        'watchers': 0,
        'watchers_count': 0
    }


def ZIPBALL(stream=True):
    from zipfile import ZipFile
    from StringIO import StringIO

    memfile = StringIO()
    zipfile = ZipFile(memfile, 'w')
    zipfile.writestr('test.txt', 'hello world')
    zipfile.close()
    memfile.seek(0)

    if stream:
        def stream_file(f):
            for b in f.read(2):
                yield b
        return stream_file(memfile)
    return memfile


def PAYLOAD(sender, repo, tag="v1.0"):
    c = dict(
        repo=repo,
        user=sender,
        url="%s/%s" % (sender, repo),
        id='4321',
        tag=tag

    )

    return {
        "action": "published",
        "release": {
            "url": "https://api.github.com/repos/%(url)s/releases/%(id)s" % c,
            "assets_url": "https://api.github.com/repos/%(url)s/releases/%(id)s/assets" % c,
            "upload_url": "https://uploads.github.com/repos/%(url)s/releases/%(id)s/assets{?name}" % c,
            "html_url": "https://github.com/%(url)s/releases/tag/%(tag)s" % c,
            "id": int(c['id']),
            "tag_name": c['tag'],
            "target_commitish": "master",
            "name": "Release name",
            "body": "",
            "draft": False,
            "author": {
                "login": "%(user)s" % c,
                "id": 1698163,
                "avatar_url": "https://avatars.githubusercontent.com/u/12345",
                "gravatar_id": "12345678",
                "url": "https://api.github.com/users/%(user)s" % c,
                "html_url": "https://github.com/%(user)s" % c,
                "followers_url": "https://api.github.com/users/%(user)s/followers" % c,
                "following_url": "https://api.github.com/users/%(user)s/following{/other_user}" % c,
                "gists_url": "https://api.github.com/users/%(user)s/gists{/gist_id}" % c,
                "starred_url": "https://api.github.com/users/%(user)s/starred{/owner}{/repo}" % c,
                "subscriptions_url": "https://api.github.com/users/%(user)s/subscriptions" % c,
                "organizations_url": "https://api.github.com/users/%(user)s/orgs" % c,
                "repos_url": "https://api.github.com/users/%(user)s/repos" % c,
                "events_url": "https://api.github.com/users/%(user)s/events{/privacy}" % c,
                "received_events_url": "https://api.github.com/users/%(user)s/received_events" % c,
                "type": "User",
                "site_admin": False
            },
            "prerelease": False,
            "created_at": "2014-02-26T08:13:42Z",
            "published_at": "2014-02-28T13:55:32Z",
            "assets": [

            ],
            "tarball_url": "https://api.github.com/repos/%(url)s/tarball/%(tag)s" % c,
            "zipball_url": "https://api.github.com/repos/%(url)s/zipball/%(tag)s" % c
        },
        "repository": {
            "id": 17202897,
            "name": repo,
            "full_name": "%(url)s" % c,
            "owner": {
                "login": "%(user)s" % c,
                "id": 1698163,
                "avatar_url": "https://avatars.githubusercontent.com/u/1698163",
                "gravatar_id": "bbc951080061fc48cae0279d27f3c015",
                "url": "https://api.github.com/users/%(user)s" % c,
                "html_url": "https://github.com/%(user)s" % c,
                "followers_url": "https://api.github.com/users/%(user)s/followers" % c,
                "following_url": "https://api.github.com/users/%(user)s/following{/other_user}" % c,
                "gists_url": "https://api.github.com/users/%(user)s/gists{/gist_id}" % c,
                "starred_url": "https://api.github.com/users/%(user)s/starred{/owner}{/repo}" % c,
                "subscriptions_url": "https://api.github.com/users/%(user)s/subscriptions" % c,
                "organizations_url": "https://api.github.com/users/%(user)s/orgs" % c,
                "repos_url": "https://api.github.com/users/%(user)s/repos" % c,
                "events_url": "https://api.github.com/users/%(user)s/events{/privacy}" % c,
                "received_events_url": "https://api.github.com/users/%(user)s/received_events" % c,
                "type": "User",
                "site_admin": False
            },
            "private": False,
            "html_url": "https://github.com/%(url)s" % c,
            "description": "Repo description.",
            "fork": True,
            "url": "https://api.github.com/repos/%(url)s" % c,
            "forks_url": "https://api.github.com/repos/%(url)s/forks" % c,
            "keys_url": "https://api.github.com/repos/%(url)s/keys{/key_id}" % c,
            "collaborators_url": "https://api.github.com/repos/%(url)s/collaborators{/collaborator}" % c,
            "teams_url": "https://api.github.com/repos/%(url)s/teams" % c,
            "hooks_url": "https://api.github.com/repos/%(url)s/hooks" % c,
            "issue_events_url": "https://api.github.com/repos/%(url)s/issues/events{/number}" % c,
            "events_url": "https://api.github.com/repos/%(url)s/events" % c,
            "assignees_url": "https://api.github.com/repos/%(url)s/assignees{/user}" % c,
            "branches_url": "https://api.github.com/repos/%(url)s/branches{/branch}" % c,
            "tags_url": "https://api.github.com/repos/%(url)s/tags" % c,
            "blobs_url": "https://api.github.com/repos/%(url)s/git/blobs{/sha}" % c,
            "git_tags_url": "https://api.github.com/repos/%(url)s/git/tags{/sha}" % c,
            "git_refs_url": "https://api.github.com/repos/%(url)s/git/refs{/sha}" % c,
            "trees_url": "https://api.github.com/repos/%(url)s/git/trees{/sha}" % c,
            "statuses_url": "https://api.github.com/repos/%(url)s/statuses/{sha}" % c,
            "languages_url": "https://api.github.com/repos/%(url)s/languages" % c,
            "stargazers_url": "https://api.github.com/repos/%(url)s/stargazers" % c,
            "contributors_url": "https://api.github.com/repos/%(url)s/contributors" % c,
            "subscribers_url": "https://api.github.com/repos/%(url)s/subscribers" % c,
            "subscription_url": "https://api.github.com/repos/%(url)s/subscription" % c,
            "commits_url": "https://api.github.com/repos/%(url)s/commits{/sha}" % c,
            "git_commits_url": "https://api.github.com/repos/%(url)s/git/commits{/sha}" % c,
            "comments_url": "https://api.github.com/repos/%(url)s/comments{/number}" % c,
            "issue_comment_url": "https://api.github.com/repos/%(url)s/issues/comments/{number}" % c,
            "contents_url": "https://api.github.com/repos/%(url)s/contents/{+path}" % c,
            "compare_url": "https://api.github.com/repos/%(url)s/compare/{base}...{head}" % c,
            "merges_url": "https://api.github.com/repos/%(url)s/merges" % c,
            "archive_url": "https://api.github.com/repos/%(url)s/{archive_format}{/ref}" % c,
            "downloads_url": "https://api.github.com/repos/%(url)s/downloads" % c,
            "issues_url": "https://api.github.com/repos/%(url)s/issues{/number}" % c,
            "pulls_url": "https://api.github.com/repos/%(url)s/pulls{/number}" % c,
            "milestones_url": "https://api.github.com/repos/%(url)s/milestones{/number}" % c,
            "notifications_url": "https://api.github.com/repos/%(url)s/notifications{?since,all,participating}" % c,
            "labels_url": "https://api.github.com/repos/%(url)s/labels{/name}" % c,
            "releases_url": "https://api.github.com/repos/%(url)s/releases{/id}" % c,
            "created_at": "2014-02-26T07:39:11Z",
            "updated_at": "2014-02-28T13:55:32Z",
            "pushed_at": "2014-02-28T13:55:32Z",
            "git_url": "git://github.com/%(url)s.git" % c,
            "ssh_url": "git@github.com:%(url)s.git" % c,
            "clone_url": "https://github.com/%(url)s.git" % c,
            "svn_url": "https://github.com/%(url)s" % c,
            "homepage": None,
            "size": 388,
            "stargazers_count": 0,
            "watchers_count": 0,
            "language": "Python",
            "has_issues": False,
            "has_downloads": True,
            "has_wiki": True,
            "forks_count": 0,
            "mirror_url": None,
            "open_issues_count": 0,
            "forks": 0,
            "open_issues": 0,
            "watchers": 0,
            "default_branch": "master",
            "master_branch": "master"
        },
        "sender": {
            "login": "%(user)s" % c,
            "id": 1698163,
            "avatar_url": "https://avatars.githubusercontent.com/u/1234578",
            "gravatar_id": "12345678",
            "url": "https://api.github.com/users/%(user)s" % c,
            "html_url": "https://github.com/%(user)s" % c,
            "followers_url": "https://api.github.com/users/%(user)s/followers" % c,
            "following_url": "https://api.github.com/users/%(user)s/following{/other_user}" % c,
            "gists_url": "https://api.github.com/users/%(user)s/gists{/gist_id}" % c,
            "starred_url": "https://api.github.com/users/%(user)s/starred{/owner}{/repo}" % c,
            "subscriptions_url": "https://api.github.com/users/%(user)s/subscriptions" % c,
            "organizations_url": "https://api.github.com/users/%(user)s/orgs" % c,
            "repos_url": "https://api.github.com/users/%(user)s/repos" % c,
            "events_url": "https://api.github.com/users/%(user)s/events{/privacy}" % c,
            "received_events_url": "https://api.github.com/users/%(user)s/received_events" % c,
            "type": "User",
            "site_admin": False
        }
    }


def ORG(login):
    return {
        'login': login,
        'id': 1234,
        'url': "https://api.github.com/orgs/%s" % login,
        'repos_url': "https://api.github.com/orgs/%s/repos" % login,
        'events_url': "https://api.github.com/orgs/%s/events" % login,
        'members_url': "https://api.github.com/orgs/%s/members{/member}" % login,
        'public_members_url': "https://api.github.com/orgs/%s/public_members{/member}" % login,
        'avatar_url': "https://avatars.githubusercontent.com/u/1234?"
    }


def CONTENT(owner, repo, file_, ref, data):
    import os
    from base64 import b64encode
    c = dict(
        url="%s/%s" % (owner, repo),
        owner=owner,
        repo=repo,
        file=file_,
        ref=ref,
    )

    return {
        '_links': {
            'git': 'https://api.github.com/repos/%(url)s/git/blobs/aaaffdfbead0b67bd6a5f5819c458a1215ecb0f6' % c,
            'html': 'https://github.com/%(url)s/blob/%(ref)s/%(file)s' % c,
            'self': 'https://api.github.com/repos/%(url)s/contents/%(file)s?ref=%(ref)s' % c
        },
        'content': b64encode(data),
        'encoding': 'base64',
        'git_url': 'https://api.github.com/repos/%(url)s/git/blobs/aaaffdfbead0b67bd6a5f5819c458a1215ecb0f6' % c,
        'html_url': 'https://github.com/%(url)s/blob/%(ref)s/%(file)s' % c,
        'name': os.path.basename(file_),
        'path': file_,
        'sha': 'aaaffdfbead0b67bd6a5f5819c458a1215ecb0f6',
        'size': 1209,
        'type': 'file',
        'url': 'https://api.github.com/repos/%(url)s/contents/%(file)s?ref=%(ref)s' % c,
    }
