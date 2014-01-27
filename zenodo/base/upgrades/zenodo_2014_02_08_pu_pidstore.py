# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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

from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from sqlalchemy.dialects import mysql

depends_on = [u'zenodo_2014_02_08_pu_community']


def info():
    return "Upgrade persistent identifier store to PU-branch"


def do_upgrade():
    """ Implement your upgrades here  """
    op.rename_table('pid', 'pidSTORE')
    op.drop_index('idx_object_type_id', 'pidSTORE')
    op.alter_column(
        'pidSTORE', 'type',
        new_column_name='pid_type',
        existing_type=mysql.VARCHAR(length=6),
        nullable=False,
        existing_server_default='')
    op.alter_column(
        'pidSTORE', 'pid',
        new_column_name='pid_value',
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
        existing_server_default='')
    op.alter_column(
        'pidSTORE', 'object_id',
        new_column_name='object_value',
        existing_type=mysql.VARCHAR(length=255),
        nullable=True,
        existing_server_default='')
    op.add_column(
        'pidSTORE',
        db.Column('pid_provider', db.String(length=255), nullable=False)
    )
    # op.create_index(
    #     'idx_object', 'pidSTORE', ['object_type', 'object_value'],
    #     unique=False
    # )
