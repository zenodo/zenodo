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

from __future__ import absolute_import, print_function, unicode_literals

import uuid

from flask import current_app
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_github.api import GitHubRelease
from invenio_github.models import Release, ReleaseStatus
from invenio_github.utils import get_contributors, get_owner
from invenio_indexer.api import RecordIndexer
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from werkzeug.utils import cached_property

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.deposit.tasks import datacite_register
from zenodo.modules.records.api import ZenodoRecord

from ..deposit.loaders import legacyjson_v1_translator
from ..jsonschemas.utils import current_jsonschemas
from zenodo.modules.github.tasks import send_github_event


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

    @property
    def repo_model(self):
        """Return repository model from relationship."""
        return self.model.repository

    @cached_property
    def recid(self):
        """Get RECID object for the Release record."""
        if self.record:
            return PersistentIdentifier.get('recid', str(self.record['recid']))

    def publish(self):
        """Publish GitHub release as record."""
        id_ = uuid.uuid4()
        deposit_metadata = dict(self.metadata)
        deposit = None
        try:
            db.session.begin_nested()
            # TODO: Add filter on Published releases
            previous_releases = self.model.repository.releases.filter_by(
                status=ReleaseStatus.PUBLISHED)
            versioning = None
            stashed_draft_child = None
            if previous_releases.count():
                last_release = previous_releases.order_by(
                        Release.created.desc()).first()
                last_recid = PersistentIdentifier.get(
                    'recid', last_release.record['recid'])
                versioning = PIDVersioning(child=last_recid)
                last_record = ZenodoRecord.get_record(
                    versioning.last_child.object_uuid)
                deposit_metadata['conceptrecid'] = last_record['conceptrecid']
                if 'conceptdoi' not in last_record:
                    last_depid = PersistentIdentifier.get(
                        'depid', last_record['_deposit']['id'])
                    last_deposit = ZenodoDeposit.get_record(
                        last_depid.object_uuid)
                    last_deposit = last_deposit.registerconceptdoi()
                    last_recid, last_record = last_deposit.fetch_published()
                deposit_metadata['conceptdoi'] = last_record['conceptdoi']
                if last_record.get('communities'):
                    deposit_metadata.setdefault('communities',
                                                last_record['communities'])
                if versioning.draft_child:
                    stashed_draft_child = versioning.draft_child
                    versioning.remove_draft_child()

            deposit = self.deposit_class.create(deposit_metadata, id_=id_)

            deposit['_deposit']['created_by'] = self.event.user_id
            deposit['_deposit']['owners'] = [self.event.user_id]

            # Fetch the deposit files
            for key, url in self.files:
                # Make a HEAD request to get GitHub to compute the
                # Content-Length.
                res = self.gh.api.session.head(url, allow_redirects=True)
                # Now, download the file
                res = self.gh.api.session.get(url, stream=True,
                                              allow_redirects=True)
                if res.status_code != 200:
                    raise Exception(
                        "Could not retrieve archive from GitHub: {url}"
                        .format(url=url)
                    )

                size = int(res.headers.get('Content-Length', 0))
                ObjectVersion.create(
                    bucket=deposit.files.bucket,
                    key=key,
                    stream=res.raw,
                    size=size or None,
                    mimetype=res.headers.get('Content-Type'),
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
            recid_pid, record = deposit.fetch_published()
            self.model.recordmetadata = record.model
            if versioning and stashed_draft_child:
                versioning.insert_draft_child(stashed_draft_child)
            record_id = str(record.id)
            db.session.commit()

            # Send Datacite DOI registration task
            if current_app.config['DEPOSIT_DATACITE_MINTING_ENABLED']:
                datacite_register.delay(recid_pid.pid_value, record_id)

            if current_app.config['GITHUB_ASCLEPIAS_BROKER_EVENTS_ENABLED']:
                release_payload = self.event.payload
                task = send_github_event.si(deposit_metadata=deposit_metadata, release_payload=release_payload)
                task.apply_async()

            # Index the record
            RecordIndexer().index_by_id(record_id)

        except Exception:
            db.session.rollback()
            # Remove deposit from index since it was not commited.
            if deposit and deposit.id:
                try:
                    RecordIndexer().delete(deposit)
                except Exception:
                    current_app.logger.exception(
                        "Failed to remove uncommited deposit from index.")
            raise
