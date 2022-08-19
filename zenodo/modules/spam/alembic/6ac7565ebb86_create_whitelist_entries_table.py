# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2022 CERN.
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

"""Create files REST tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6ac7565ebb86'
down_revision = None
branch_labels =  (u'zenodo_spam',)
depends_on = '9848d0149abd'  # invenio_accounts: create users table


def upgrade():
    """Upgrade database."""
    op.create_table(
        'safelist_entries',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            [u'accounts_user.id'],
            ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'created',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('safelist_entries')
