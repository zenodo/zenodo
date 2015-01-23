# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op

depends_on = []


def info():
    return "Create accessrequests tables."


def do_upgrade():
    op.create_table(
        'accreqREQUEST',
        db.Column('id', db.Integer(display_width=15), nullable=False),
        db.Column('status', db.String(length=1),
                  nullable=False),
        db.Column('receiver_user_id', db.Integer(display_width=15),
                  nullable=False),
        db.Column('sender_user_id', db.Integer(display_width=15),
                  nullable=True),
        db.Column('sender_full_name', db.String(length=255), nullable=False),
        db.Column('sender_email', db.String(length=255), nullable=False),
        db.Column('recid', db.Integer(display_width=15), nullable=False),
        db.Column('created', db.DateTime(), nullable=False),
        db.Column('modified', db.DateTime(), nullable=False),
        db.Column('justification', db.Text(), nullable=False),
        db.Column('message', db.Text(), nullable=False),
        db.Column('link_id', db.Integer(display_width=15), nullable=True),
        db.ForeignKeyConstraint(['receiver_user_id'], [u'user.id'], ),
        db.ForeignKeyConstraint(['sender_user_id'], [u'user.id'], ),
        db.ForeignKeyConstraint(['link_id'], [u'accreqLINK.id'], ),
        db.PrimaryKeyConstraint('id'),
        mysql_charset='utf8',
        mysql_engine='MyISAM'
    )
    op.create_index(
        op.f('ix_accreqREQUEST_created'), 'accreqREQUEST', ['created'],
        unique=False)
    op.create_index(
        op.f('ix_accreqREQUEST_recid'), 'accreqREQUEST', ['recid'],
        unique=False)
    op.create_index(
        op.f('ix_accreqREQUEST_status'), 'accreqREQUEST', ['status'],
        unique=False)

    op.create_table(
        'accreqLINK',
        db.Column('id', db.Integer(display_width=15), nullable=False),
        db.Column('token', db.Text(), nullable=False),
        db.Column('owner_user_id', db.Integer(display_width=15),
                  nullable=False),
        db.Column('created', db.DateTime(), nullable=False),
        db.Column('expires_at', db.DateTime(), nullable=True),
        db.Column('revoked_at', db.DateTime(), nullable=True),
        db.Column('title', db.String(length=255), nullable=False),
        db.Column('description', db.Text(), nullable=False),
        db.ForeignKeyConstraint(['owner_user_id'], [u'user.id'], ),
        db.PrimaryKeyConstraint('id'),
        mysql_charset='utf8',
        mysql_engine='MyISAM'
    )
    op.create_index(
        op.f('ix_accreqLINK_created'), 'accreqLINK', ['created'], unique=False)
    op.create_index(
        op.f('ix_accreqLINK_revoked_at'), 'accreqLINK', ['revoked_at'],
        unique=False)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
