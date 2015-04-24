# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import warnings
from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from invenio.utils.text import wait_for_user


depends_on = []


def info():
    return "Short description of upgrade displayed to end-user"


def do_upgrade():
    """Implement your upgrades here."""
    op.create_table('quotaUSAGE',
    db.Column('id', db.Integer(display_width=15), nullable=False),
    db.Column('object_type', db.String(length=40), nullable=True),
    db.Column('object_id', db.String(length=250), nullable=True),
    db.Column('metric', db.String(length=40), nullable=True),
    db.Column('value', db.BigInteger(), nullable=False),
    db.Column('modified', db.DateTime(), nullable=False),
    db.PrimaryKeyConstraint('id'),
    db.UniqueConstraint('object_type', 'object_id', 'metric'),
    mysql_charset='utf8',
    mysql_engine='MyISAM'
    )
    op.create_index(op.f('ix_quotaUSAGE_object_id'), 'quotaUSAGE', ['object_id'], unique=False)
    op.create_index(op.f('ix_quotaUSAGE_object_type'), 'quotaUSAGE', ['object_type'], unique=False)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
