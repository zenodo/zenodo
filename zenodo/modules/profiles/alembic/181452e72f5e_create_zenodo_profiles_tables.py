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

"""Create Zenodo profiles tables."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '181452e72f5e'
down_revision = '4efa0316e2b3'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'zenodo_profiles_profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('affiliation', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('show_profile', sa.Boolean(name='show_profile'),
                  nullable=True),
        sa.Column('allow_contact_owner',
                  sa.Boolean(name='allow_contact_owner'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['accounts_user.id'],
                                name='fk_zenodo_profiles_profiles_user_id'),
        sa.PrimaryKeyConstraint('user_id', name='pk_zenodo_profiles_profiles')
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('zenodo_profiles_profiles')
