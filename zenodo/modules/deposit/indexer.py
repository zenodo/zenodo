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

"""Record modification prior to indexing."""

from __future__ import absolute_import, print_function

from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record


def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES.

    :param sender: Sender of the signal.
    :param json: JSON to be passed for the elastic search.
    :type json: `invenio_records.api.Record`
    :param record: Indexed record.
    :type record: `invenio_records.api.Record`
    :param index: Elasticsearch index.
    :type index: str
    """
    # Inject timestamp into record.
    if not index.startswith('deposits-records-'):
        return
    json['_created'] = record.created
    if record['_deposit']['status'] != 'published':
        json['_updated'] = record.updated
    else:
        json['_updated'] = record['_deposit']['submitted']

    if 'recid' in record['_deposit'] and \
            record['_deposit']['status'] == 'published':
        recid = record['_deposit']['recid']
        resolver = Resolver(pid_type='recid', object_type='rec',
                            getter=Record.get_record)
        rec_pid, rec = resolver.resolve(recid)
        json['title'] = rec['title']  # TODO: map record to deposit here
