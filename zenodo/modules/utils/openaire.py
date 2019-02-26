# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018-2019 CERN.
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
import re
from collections import OrderedDict
import requests

from flask import current_app
from invenio_accounts.models import User
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
                    unresolved_communities.append(dict(
                        openaire_community=openaire_community['id'],
                        zenodo_community=zenodo_community))

            comm_id = openaire_community['id']
            if mapping.get(comm_id):
                mapping[comm_id]['name'] = openaire_community['name']
                mapping[comm_id]['communities'] = zenodo_community_ids
            else:
                mapping[comm_id] = dict(name=openaire_community['name'],
                                        communities=zenodo_community_ids,
                                        types={})

        return mapping, unresolved_communities


def fetch_communities_mapping():
    """Fetch communities mapping via the OpenAIRE APIs."""
    oa_communities_url = 'https://beta.services.openaire.eu/openaire/community/communities'
    z_communities_url = 'https://beta.services.openaire.eu/openaire/community/{id}/zenodocommunities'
    mapping = {}
    res = requests.get(oa_communities_url)
    if res.ok:
        openaire_communities = res.json()
        for openaire_community in openaire_communities:
            zenodo_community_ids = []
            comm_id = openaire_community['id']
            res = requests.get(z_communities_url.format(id=comm_id))
            if res.ok:
                for z_comm in res.json():
                    if not _is_url(z_comm['zenodoid']):
                        zenodo_community_ids.append(z_comm['zenodoid'])

            mapping[comm_id] = dict(name=openaire_community['name'],
                                    communities=zenodo_community_ids,
                                    types=openaire_community['type'],
                                    primary_community=
                                    openaire_community['zenodoCommunity'],
                                    curators=openaire_community['managers'])

    return mapping


def _is_url(string):
    """Check is the string is a URL."""
    url = re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] | [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url is not None


def _community_exists(community_id):
    """Search if the community exists in Zenodo."""
    query = db.session.query(Community).filter(
        Community.id == community_id
    )
    comm = query.one_or_none()
    return comm is not None


def _fetch_community_curator_id(curators):
    """Fetch the id of the first Zenodo user in the list."""
    curator_id = None

    for curator in curators:
        query = User.query.filter_by(email=curator)
        user = query.one_or_none()
        if user:
            curator_id = user.id
        break

    return curator_id


def get_new_communites(community_mapping):
    """Return the list of the communities which are not in Zenodo.

    :param community_mapping: The community mapping
    """
    new_communities = []

    for oa_community_id in community_mapping:
        openaire_community = community_mapping[oa_community_id]
        primary_community = openaire_community['primary_community']
        if primary_community and not _community_exists(primary_community):
            curators = openaire_community['curators']
            curator_id = _fetch_community_curator_id(curators)
            new_community = dict(id=primary_community,
                                 title=openaire_community['name'],
                                 owner=curator_id)
            new_communities.append(new_community)

    return new_communities


def create_communities(new_communities):
    """Create new communities.

    :param new_communities: array of new communities. Each element of the
    array is a dictionary with the id, title and owner of the new community.
    """
    for comm in new_communities:
        if comm['owner']:
            Community.create(comm['id'],
                             user_id=comm['owner'],
                             title=comm['title'])
            db.session.commit()


def compare_community_mappings(current, new):
    """Compare the current and the new mappings of a community."""
    # 1) check if the title has changed
    # 2) check if the primary community has changed
    # 3) check if the communities have changed

    diff = {}
    if current['name'] != new['name']:
        diff['name'] = new['name']

    current_primary_community = current.get('primary_community')
    if current_primary_community != new['primary_community']:
        if current_primary_community is not None:
            raise Exception("Primary community cannot change.")
        diff['primary_community'] = new['primary_community']

    if current['communities'] != new['communities']:
        if len(new['communities']) < len(current['communities']):
            raise Exception("Communities cannot be deleted.")
        for comm in current['communities']:
            if comm not in new['communities']:
                raise Exception("Communities cannot be deleted.")
        diff['communities'] = new['communities']

    return diff


def update_communities_mapping(current_mapping, new_mapping):
    """Update communities mapping."""
    unresolved_communities = []
    updated_mapping = {}
    diff = {}

    for oa_community_id in new_mapping:
        openaire_community = new_mapping[oa_community_id]

        # here we don't check if the primary_community is a real Zenodo
        # community; this is checked in the get_new_communites() method

        zenodo_community_ids = []
        for zenodo_community in openaire_community.get('communities'):
            if _community_exists(zenodo_community):
                zenodo_community_ids.append(zenodo_community)
            else:
                unresolved_communities.append(dict(
                    openaire_community=oa_community_id,
                    zenodo_community=zenodo_community))
        openaire_community['communities'] = zenodo_community_ids

        community_types = None  # community types are not provided by the APIs
        current = current_mapping.get(oa_community_id)
        if current:
            community_types = current['types']

            # compare current and new mappings
            mapping_diff = \
                compare_community_mappings(current, openaire_community)
            if mapping_diff:
                diff[oa_community_id] = mapping_diff

        updated_mapping[oa_community_id] = dict(
            name=openaire_community['name'],
            communities=zenodo_community_ids,
            primary_community=openaire_community['primary_community'],
            types=community_types,
        )

    # the updated_mapping should be in alphabetical order
    updated_mapping = OrderedDict(sorted(updated_mapping.items()))

    return updated_mapping, diff, unresolved_communities
