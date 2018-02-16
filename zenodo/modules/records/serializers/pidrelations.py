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
# You should have received a copy of the GNU General Public Licnse
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo Serializers."""

from __future__ import absolute_import, print_function

from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier

from zenodo.modules.records.api import ZenodoRecord


def serialize_related_identifiers(pid):
    """Serialize PID Versioning relations as related_identifiers metadata."""
    pv = PIDVersioning(child=pid)
    related_identifiers = []
    if pv.exists:

        rec = ZenodoRecord.get_record(pid.get_assigned_object())
        # External DOI records don't have Concept DOI
        if 'conceptdoi' in rec:
            ri = {
                'scheme': 'doi',
                'relation': 'isVersionOf',
                'identifier': rec['conceptdoi']
            }
            related_identifiers.append(ri)

        # TODO: We do not serialize previous/next versions to
        # related identifiers because of the semantic-versioning cases
        # (e.g. GitHub releases of minor versions)
        #
        # children = pv.children.all()
        # idx = children.index(pid)
        # left = children[:idx]
        # right = children[idx + 1:]
        # for p in left:
        #     rec = ZenodoRecord.get_record(p.get_assigned_object())
        #     ri = {
        #         'scheme': 'doi',
        #         'relation': 'isNewVersionOf',
        #         'identifier': rec['doi']
        #     }
        #     related_identifiers.append(ri)

        # for p in right:
        #     rec = ZenodoRecord.get_record(p.get_assigned_object())
        #     ri = {
        #         'scheme': 'doi',
        #         'relation': 'isPreviousVersionOf',
        #         'identifier': rec['doi']
        #     }
        #     related_identifiers.append(ri)
    pv = PIDVersioning(parent=pid)
    if pv.exists:
        for p in pv.children:
            rec = ZenodoRecord.get_record(p.get_assigned_object())
            ri = {
                'scheme': 'doi',
                'relation': 'hasVersion',
                'identifier': rec['doi']
            }
            related_identifiers.append(ri)
    return related_identifiers


def preprocess_related_identifiers(pid, record, result):
    """Preprocess related identifiers for record serialization.

    Resolves the passed pid to the proper `recid` in order to add related
    identifiers from PID relations.
    """
    recid_value = record.get('recid')
    if pid.pid_type == 'doi' and pid.pid_value == record.get('conceptdoi'):
        recid_value = record.get('conceptrecid')
        result['metadata']['doi'] = record.get('conceptdoi')
    recid = (pid if pid.pid_value == recid_value else
             PersistentIdentifier.get(pid_type='recid', pid_value=recid_value))

    if recid.pid_value == record.get('conceptrecid'):
        pv = PIDVersioning(parent=recid)
    else:
        pv = PIDVersioning(child=recid)

    # Serialize PID versioning as related identifiers
    if pv.exists:
        rels = serialize_related_identifiers(recid)
        if rels:
            result['metadata'].setdefault(
                'related_identifiers', []).extend(rels)
    return result
