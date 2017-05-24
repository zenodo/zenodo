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

"""Utilities for Zenodo-Auditor."""


import logging
from collections import Counter
from logging.handlers import MemoryHandler

from flask import current_app, url_for
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.models import RecordMetadata
from mock import MagicMock

from ..records.api import ZenodoRecord


def all_records():
    """Return a ZenodoRecord generator with all records."""
    records = (db.session.query(RecordMetadata)
               .join(PersistentIdentifier,
                     RecordMetadata.id == PersistentIdentifier.object_uuid)
               .filter(PersistentIdentifier.pid_type == 'recid',
                       PersistentIdentifier.status == PIDStatus.REGISTERED))
    return (ZenodoRecord(data=r.json, model=r) for r in records)


class tree(dict):
    """Self-vivified dictionary."""

    def __missing__(self, key):
        """Return a new instance of self."""
        value = self[key] = type(self)()
        return value


def duplicates(l):
    """Return duplicate elements from an iterable."""
    return [i for i, c in Counter(l).items() if c > 1]


def sickle_requests_get_mock():
    """Return a mock `request.get` for `sickle` that uses `Flask.test_client`.

    Because `sickle.Sickle` is strongly dependent on the `requests` library to
    make all its OAI-PMH harvesting calls, it is not possible to use it for
    local usage without running a live instance of Invenio-OAIServer. To bypass
    this we are making a function mock that makes a request using the
    `Flask.test_client`, and returns a mock containing the text response.
    """
    def get(endpoint, params, **kwargs):
        """Mock `request.get` method."""
        with current_app.test_request_context():
            with current_app.test_client() as client:
                if endpoint == 'http://auditor/oai2d':
                    oai_url = url_for('invenio_oaiserver.response', **params)
                    res = client.get(oai_url)

                    mock_res = MagicMock()
                    mock_res.text = res.get_data(as_text=True)
                    return mock_res
    return MagicMock(side_effect=get)


def get_file_logger(logfile, audit_type, audit_id):
    """Return a buffered file logger."""
    logger = logging.getLogger('zenodo.auditor.{type}.{id}'
                               .format(type=audit_type, id=audit_id))
    if logfile:
        file_handler = logging.FileHandler(logfile, mode='w')
        logger.addHandler(MemoryHandler(100, target=file_handler))
    return logger
