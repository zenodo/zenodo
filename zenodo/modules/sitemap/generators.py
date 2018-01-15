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

"""Sitemap generators."""

from __future__ import absolute_import, print_function

import arrow
from flask import current_app, url_for
from invenio_communities.models import Community
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.models import RecordMetadata


def _sitemapdtformat(dt):
    """Convert a datetime to a W3 Date and Time format.

    Converts the date to a minute-resolution datetime timestamp with a special
    UTC designator 'Z'. See more information at
    https://www.w3.org/TR/NOTE-datetime.
    """
    adt = arrow.Arrow.fromdatetime(dt).to('utc')
    return adt.format('YYYY-MM-DDTHH:MM:SS') + 'Z'


def records_generator():
    """Generate the records links."""
    q = (db.session.query(PersistentIdentifier, RecordMetadata)
         .join(RecordMetadata,
               RecordMetadata.id == PersistentIdentifier.object_uuid)
         .filter(PersistentIdentifier.status == PIDStatus.REGISTERED,
                 PersistentIdentifier.pid_type == 'recid'))

    scheme = current_app.config['ZENODO_SITEMAP_URL_SCHEME']
    for pid, rm in q.yield_per(1000):
        yield {
            'loc': url_for('invenio_records_ui.recid', pid_value=pid.pid_value,
                           _external=True, _scheme=scheme),
            'lastmod': _sitemapdtformat(rm.updated)
        }


def communities_generator():
    """Generate the communities links."""
    q = Community.query.filter(Community.deleted_at.is_(None))
    scheme = current_app.config['ZENODO_SITEMAP_URL_SCHEME']
    for comm in q.yield_per(1000):
        for endpoint in 'detail', 'search', 'about':
            yield {
                'loc': url_for('invenio_communities.{}'.format(endpoint),
                               community_id=comm.id, _external=True,
                               _scheme=scheme),
                'lastmod': _sitemapdtformat(comm.updated)
            }


generator_fns = [
    records_generator,
    communities_generator,
]
