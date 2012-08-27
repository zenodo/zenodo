# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2008, 2009, 2010, 2011, 2012 CERN.
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

from invenio.dbmigrator_utils import DbMigration, run_sql_ignore, run_tabcreate
from invenio.dbquery import run_sql

class Migration( DbMigration ):
    """ Adding field userid to aidUSERINPUTLOG """
    depends_on = ['baseline','0001_add_session_expiry_index']
    
    def forward(self):
        run_sql("ALTER TABLE aidUSERINPUTLOG ADD COLUMN userid int AFTER timestamp")
        run_sql("ALTER TABLE aidUSERINPUTLOG ADD KEY `userid-b` (userid)")
