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

"""Zenodo GitHub API."""

from __future__ import absolute_import

from flask import current_app
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_github.api import GitHubRelease
from invenio_github.utils import get_contributors, get_owner

from ..deposit.loaders import legacyjson_v1_translator
from ..jsonschemas.utils import current_jsonschemas


class ZenodoGitHubRelease(GitHubRelease):
    """Zenodo GitHub Release."""

    @property
    def metadata(self):
        """Return extracted metadata."""
        output = dict(self.defaults)
        output.update(self.extra_metadata)

        # Add creators if not specified
        if 'creators' not in output:
            output['creators'] = get_contributors(self.gh.api,
                                                  self.repository['id'])
        if not output['creators']:
            output['creators'] = get_owner(self.gh.api, self.author)
        if not output['creators']:
            output['creators'] = [dict(name='Unknown', affiliation='')]

        return legacyjson_v1_translator({'metadata': output})

    def publish(self):
        """Publish GitHub release as record."""
        with db.session.begin_nested():
            deposit = self.deposit_class.create(self.metadata)
            deposit['_deposit']['created_by'] = self.event.user_id
            deposit['_deposit']['owners'] = [self.event.user_id]

            # Fetch the deposit files
            for key, url in self.files:
                # Make a HEAD request to get GitHub to compute the
                # content-length.
                self.gh.api.session.head(url)
                # Now, download the file
                res = self.gh.api.session.get(url, stream=True)
                ObjectVersion.create(
                    bucket=deposit.files.bucket,
                    key=key,
                    stream=res.raw,
                    size=res.headers['Content-Length'],
                )

            # GitHub-specific SIP store agent
            sip_agent = {
                '$schema': current_jsonschemas.path_to_url(
                    current_app.config['SIPSTORE_GITHUB_AGENT_JSONSCHEMA']),
                'user_id': self.event.user_id,
                'github_id': self.release['author']['id'],
                'email': self.gh.account.user.email,
            }
            deposit.publish(user_id=self.event.user_id, sip_agent=sip_agent)
            self.model.recordmetadata = deposit.model
