# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Communities utilities."""

import csv

from flask import current_app
from invenio_communities.models import Community
from invenio_db import db


class OpenAIRECommunitiesMappingUpdater:
    """Utility class to update OpenAIRE communities mapping."""

    def __init__(self, path):
        """Initialize the OpenAIRE communities updater."""
        self.path = path

    def _parse_line(self, line):
        community_id = line[0]
        community_name = line[1]
        zenodo_communities = line[2].split(';') if len(line) == 3 else []

        openaire_community = dict(id=community_id,
                                  name=community_name,
                                  communities=zenodo_communities)
        return openaire_community

    @property
    def _communities_iterator(self):
        with open(self.path, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            csv_reader.next()  # skip csv header
            for line in csv_reader:
                yield self._parse_line(line)

    def update_communities_mapping(self):
        """Update communities mapping."""
        mapping = current_app.config['ZENODO_OPENAIRE_COMMUNITIES']
        unresolved_communities = []

        for openaire_community in self._communities_iterator:
            zenodo_community_ids = []
            for zenodo_community in openaire_community.get('communities'):
                # search for the corresponding community in Zenodo
                query = db.session.query(Community).filter(
                    Community.title.like(zenodo_community + '%')
                )
                comm = query.one_or_none()
                if comm is not None:
                    zenodo_community_ids.append(comm.id)
                else:
                    unresolved_communities.append(zenodo_community)

            comm_id = openaire_community['id']
            mapping[comm_id]['name'] = openaire_community['name']
            mapping[comm_id]['communities'] = zenodo_community_ids

        return mapping, unresolved_communities
