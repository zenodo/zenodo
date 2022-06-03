# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create files REST tables."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2e97565eba73'
down_revision = None
branch_labels =  (u'zenodo_spam',)
depends_on = '9848d0149abd'  # invenio_accounts: create users table


def upgrade():
    """Upgrade database."""

    op.create_table(
        'safelist_entries',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['accounts_user'],
            [u'accounts_user.id'],
            ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.Column(
            'created',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False
        )
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('safelist_entries')
