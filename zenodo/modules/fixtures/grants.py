# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""CLI for Zenodo fixtures."""

from __future__ import absolute_import, print_function

from invenio_db import db
from invenio_openaire.minters import funder_minter, grant_minter
from invenio_records.api import Record

from .utils import read_json


def loadfp6funders(force=False):
    """Load FP6 funder fixtures."""
    data = read_json('data/funders.json')
    try:
        for f in data:
            r = Record.create(f)
            funder_minter(r.id, r)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise



def loadfp6grants(force=False):
    """Load FP6 grant fixtures."""
    data = read_json('data/grants.json')
    try:
        for g in data:
            r = Record.create(g)
            grant_minter(r.id, r)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
