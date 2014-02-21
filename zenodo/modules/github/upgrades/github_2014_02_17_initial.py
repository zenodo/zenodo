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

depends_on = []


def info():
    return "Short description of upgrade displayed to end-user"


def do_upgrade():
    """ Implement your upgrades here  """
    op.create_table(
        'oauth_tokens',
        db.Column('id', db.Integer(display_width=100), nullable=False),
        db.Column('client_id', db.String(length=255), nullable=False),
        db.Column('user_id', db.Integer(display_width=15), nullable=False),
        db.Column('access_token', db.Text(), nullable=False),
        db.Column('extra_data', db.JSON, nullable=True),
        db.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        db.PrimaryKeyConstraint('id'),
        mysql_charset='utf8',
        mysql_engine='MyISAM'
    )
