# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from sqlalchemy.dialects import mysql

depends_on = [
    'openaire_2013_10_11_webdeposit_migration',
    'invenio_2013_08_22_hstRECORD_affected_fields',
]


def info():
    return "Misc pu-branch upgrades"


def do_upgrade():
    # History
    op.add_column('hstDOCUMENT', db.Column(
        'id', mysql.INTEGER(display_width=15), nullable=False))
    op.add_column('hstRECORD', db.Column(
        'id', mysql.INTEGER(display_width=15), nullable=False))

    op.alter_column('hstRECORD', 'affected_fields',
                    existing_type=mysql.TEXT(),
                    nullable=True)

    # OAI Harvest
    op.drop_column('oaiHARVEST', u'bibconvertcfgfile')
    op.drop_column('oaiHARVEST', u'bibfilterprogram')

    # xtrJOB
    op.drop_column('xtrJOB', u'last_recid')

    # Record
    op.add_column("bibrec", db.Column("additional_info", db.JSON))
