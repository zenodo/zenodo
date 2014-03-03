# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio.testsuite import InvenioTestCase
from mock import MagicMock, patch
from cStringIO import StringIO
import json

response = MagicMock()
response.raw = StringIO("TEST")
response.status_code = 200


class PayloadExtractionTestCase(InvenioTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('requests.get', return_value=response)
    def test_extract_files(self, get):
        from ..tasks import extract_files

        files = extract_files(PAYLOAD_EXAMPLE)
        assert len(files) == 1

        fileobj, filename = files[0]
        assert filename == "decouple-v1.1.4.zip"

    def test_extract_metadata(self):
        from ..tasks import extract_metadata

        content = MagicMock()
        content.decoded = json.dumps(dict(upload_type="dataset"))

        repo = MagicMock()
        repo.contents = MagicMock(return_value=content)

        gh = MagicMock()
        gh.repository = MagicMock(return_value=repo)

        metadata = extract_metadata(gh, PAYLOAD_EXAMPLE)
        assert metadata['upload_type'] == 'dataset'



PAYLOAD_EXAMPLE = {
    "action": "published",
    "release": {
        "url": "https://api.github.com/repos/lnielsen-cern/decouple/releases/204424",
        "assets_url": "https://api.github.com/repos/lnielsen-cern/decouple/releases/204424/assets",
        "upload_url": "https://uploads.github.com/repos/lnielsen-cern/decouple/releases/204424/assets{?name}",
        "html_url": "https://github.com/lnielsen-cern/decouple/releases/tag/v1.1.4",
        "id": 204424,
        "tag_name": "v1.1.4",
        "target_commitish": "master",
        "name": "GitHub/Zenodo release test",
        "body": "",
        "draft": False,
        "author": {
            "login": "lnielsen-cern",
            "id": 1698163,
            "avatar_url": "https://avatars.githubusercontent.com/u/1698163",
            "gravatar_id": "bbc951080061fc48cae0279d27f3c015",
            "url": "https://api.github.com/users/lnielsen-cern",
            "html_url": "https://github.com/lnielsen-cern",
            "followers_url": "https://api.github.com/users/lnielsen-cern/followers",
            "following_url": "https://api.github.com/users/lnielsen-cern/following{/other_user}",
            "gists_url": "https://api.github.com/users/lnielsen-cern/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/lnielsen-cern/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/lnielsen-cern/subscriptions",
            "organizations_url": "https://api.github.com/users/lnielsen-cern/orgs",
            "repos_url": "https://api.github.com/users/lnielsen-cern/repos",
            "events_url": "https://api.github.com/users/lnielsen-cern/events{/privacy}",
            "received_events_url": "https://api.github.com/users/lnielsen-cern/received_events",
            "type": "User",
            "site_admin": False
        },
        "prerelease": False,
        "created_at": "2014-02-26T08:13:42Z",
        "published_at": "2014-02-28T13:55:32Z",
        "assets": [

        ],
        "tarball_url": "https://api.github.com/repos/lnielsen-cern/decouple/tarball/v1.1.4",
        "zipball_url": "https://api.github.com/repos/lnielsen-cern/decouple/zipball/v1.1.4"
    },
    "repository": {
        "id": 17202897,
        "name": "decouple",
        "full_name": "lnielsen-cern/decouple",
        "owner": {
            "login": "lnielsen-cern",
            "id": 1698163,
            "avatar_url": "https://avatars.githubusercontent.com/u/1698163",
            "gravatar_id": "bbc951080061fc48cae0279d27f3c015",
            "url": "https://api.github.com/users/lnielsen-cern",
            "html_url": "https://github.com/lnielsen-cern",
            "followers_url": "https://api.github.com/users/lnielsen-cern/followers",
            "following_url": "https://api.github.com/users/lnielsen-cern/following{/other_user}",
            "gists_url": "https://api.github.com/users/lnielsen-cern/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/lnielsen-cern/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/lnielsen-cern/subscriptions",
            "organizations_url": "https://api.github.com/users/lnielsen-cern/orgs",
            "repos_url": "https://api.github.com/users/lnielsen-cern/repos",
            "events_url": "https://api.github.com/users/lnielsen-cern/events{/privacy}",
            "received_events_url": "https://api.github.com/users/lnielsen-cern/received_events",
            "type": "User",
            "site_admin": False
        },
        "private": False,
        "html_url": "https://github.com/lnielsen-cern/decouple",
        "description": "Decouple and recouple.",
        "fork": True,
        "url": "https://api.github.com/repos/lnielsen-cern/decouple",
        "forks_url": "https://api.github.com/repos/lnielsen-cern/decouple/forks",
        "keys_url": "https://api.github.com/repos/lnielsen-cern/decouple/keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/lnielsen-cern/decouple/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/lnielsen-cern/decouple/teams",
        "hooks_url": "https://api.github.com/repos/lnielsen-cern/decouple/hooks",
        "issue_events_url": "https://api.github.com/repos/lnielsen-cern/decouple/issues/events{/number}",
        "events_url": "https://api.github.com/repos/lnielsen-cern/decouple/events",
        "assignees_url": "https://api.github.com/repos/lnielsen-cern/decouple/assignees{/user}",
        "branches_url": "https://api.github.com/repos/lnielsen-cern/decouple/branches{/branch}",
        "tags_url": "https://api.github.com/repos/lnielsen-cern/decouple/tags",
        "blobs_url": "https://api.github.com/repos/lnielsen-cern/decouple/git/blobs{/sha}",
        "git_tags_url": "https://api.github.com/repos/lnielsen-cern/decouple/git/tags{/sha}",
        "git_refs_url": "https://api.github.com/repos/lnielsen-cern/decouple/git/refs{/sha}",
        "trees_url": "https://api.github.com/repos/lnielsen-cern/decouple/git/trees{/sha}",
        "statuses_url": "https://api.github.com/repos/lnielsen-cern/decouple/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/lnielsen-cern/decouple/languages",
        "stargazers_url": "https://api.github.com/repos/lnielsen-cern/decouple/stargazers",
        "contributors_url": "https://api.github.com/repos/lnielsen-cern/decouple/contributors",
        "subscribers_url": "https://api.github.com/repos/lnielsen-cern/decouple/subscribers",
        "subscription_url": "https://api.github.com/repos/lnielsen-cern/decouple/subscription",
        "commits_url": "https://api.github.com/repos/lnielsen-cern/decouple/commits{/sha}",
        "git_commits_url": "https://api.github.com/repos/lnielsen-cern/decouple/git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/lnielsen-cern/decouple/comments{/number}",
        "issue_comment_url": "https://api.github.com/repos/lnielsen-cern/decouple/issues/comments/{number}",
        "contents_url": "https://api.github.com/repos/lnielsen-cern/decouple/contents/{+path}",
        "compare_url": "https://api.github.com/repos/lnielsen-cern/decouple/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/lnielsen-cern/decouple/merges",
        "archive_url": "https://api.github.com/repos/lnielsen-cern/decouple/{archive_format}{/ref}",
        "downloads_url": "https://api.github.com/repos/lnielsen-cern/decouple/downloads",
        "issues_url": "https://api.github.com/repos/lnielsen-cern/decouple/issues{/number}",
        "pulls_url": "https://api.github.com/repos/lnielsen-cern/decouple/pulls{/number}",
        "milestones_url": "https://api.github.com/repos/lnielsen-cern/decouple/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/lnielsen-cern/decouple/notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/lnielsen-cern/decouple/labels{/name}",
        "releases_url": "https://api.github.com/repos/lnielsen-cern/decouple/releases{/id}",
        "created_at": "2014-02-26T07:39:11Z",
        "updated_at": "2014-02-28T13:55:32Z",
        "pushed_at": "2014-02-28T13:55:32Z",
        "git_url": "git://github.com/lnielsen-cern/decouple.git",
        "ssh_url": "git@github.com:lnielsen-cern/decouple.git",
        "clone_url": "https://github.com/lnielsen-cern/decouple.git",
        "svn_url": "https://github.com/lnielsen-cern/decouple",
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
        "login": "lnielsen-cern",
        "id": 1698163,
        "avatar_url": "https://avatars.githubusercontent.com/u/1698163",
        "gravatar_id": "bbc951080061fc48cae0279d27f3c015",
        "url": "https://api.github.com/users/lnielsen-cern",
        "html_url": "https://github.com/lnielsen-cern",
        "followers_url": "https://api.github.com/users/lnielsen-cern/followers",
        "following_url": "https://api.github.com/users/lnielsen-cern/following{/other_user}",
        "gists_url": "https://api.github.com/users/lnielsen-cern/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/lnielsen-cern/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/lnielsen-cern/subscriptions",
        "organizations_url": "https://api.github.com/users/lnielsen-cern/orgs",
        "repos_url": "https://api.github.com/users/lnielsen-cern/repos",
        "events_url": "https://api.github.com/users/lnielsen-cern/events{/privacy}",
        "received_events_url": "https://api.github.com/users/lnielsen-cern/received_events",
        "type": "User",
        "site_admin": False
    }
}
