# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Profile records."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl.query import Q
from invenio_search.api import RecordsSearch


class ResearcherRecordsSearch(RecordsSearch):
    """Search class for records that goes on the profile page."""

    class Meta(object):
        """Default index and filter for profile page search."""

        index = 'records'

    def __init__(self, user_id=None, orcid_id=None, **kwargs):
        """Constructor function."""
        args = []
        if user_id:
            args.append(Q('term', **{'owners': user_id}))
        if orcid_id:
            args.append(Q('term', **{'creators.orcid': orcid_id}))

        self.Meta.default_filter = Q('bool', must=[
            Q('bool', should=args),
            Q('term', **{'relations.version.is_last': True})])
        super(ResearcherRecordsSearch, self).__init__(**kwargs)
