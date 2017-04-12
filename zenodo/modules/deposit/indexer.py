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

import copy

from .api import ZenodoDeposit

from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier

from invenio_pidrelations.proxies import current_pidrelations
from invenio_pidrelations.serializers.utils import serialize_relations
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidrelations.contrib.records import index_siblings


def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES.

    In order to avoid that a record and published deposit differs (e.g. if an
    embargo task updates the record), every time we index a record we also
    index the deposit and overwrite the content with that of the record.

    :param sender: Sender of the signal.
    :param json: JSON to be passed for the elastic search.
    :type json: `invenio_records.api.Deposit`
    :param record: Indexed deposit record.
    :type record: `invenio_records.api.Deposit`
    :param index: Elasticsearch index name.
    :type index: str
    """
    if not index.startswith('deposits-records-'):
        return

    if not isinstance(record, ZenodoDeposit):
        record = ZenodoDeposit(record, model=record.model)

    if record['_deposit']['status'] == 'published':
        schema = json['$schema']

        pub_record = record.fetch_published()[1]

        # Temporarily set to draft mode to ensure that `clear` can be called
        json['_deposit']['status'] = 'draft'
        json.clear()
        json.update(copy.deepcopy(pub_record.replace_refs()))

        # Set back to published mode and restore schema.
        json['_deposit']['status'] = 'published'
        json['$schema'] = schema
        json['_updated'] = pub_record.updated
    else:
        json['_updated'] = record.updated
    json['_created'] = record.created

    # Compute filecount and total file size
    files = json.get('_files', [])
    json['filecount'] = len(files)
    json['size'] = sum([f.get('size', 0) for f in files])

    recid = record.get('recid')
    if recid:
        pid = PersistentIdentifier.get('recid', recid)
        pv = PIDVersioning(child=pid)
        if pv.exists:
            relations = serialize_relations(pid)
            if pv.draft_child_deposit:
                if pv.draft_child_deposit.pid_value \
                    == record['_deposit']['id']:
                    is_last = True
                else:
                    is_last = False
                relations['version'][0]['is_last'] = is_last
        else:
            relations = {'version': [{'is_last': True, 'index': 0}, ]}
        if relations:
            json['relations'] = relations


def index_versioned_record_siblings(sender, action=None, pid=None,
                                    deposit=None):
    """Send previous version of published record for indexing."""
    first_publish = (deposit.get('_deposit', {}).get('pid', {})
                 .get('revision_id')) == 0
    if action == "publish" and first_publish:
        recid_pid, _ = deposit.fetch_published()
        print('sending for indexing siblings of', recid_pid)
        index_siblings(recid_pid, only_neighbors=True)
