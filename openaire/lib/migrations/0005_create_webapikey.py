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
    """ Create table webapikey """
    depends_on = ['baseline','0004_create_bibdocfsinfo']
    
    def forward(self):
        run_sql("""
CREATE TABLE IF NOT EXISTS webapikey (
  id varchar(150) NOT NULL,
  secret varchar(150) NOT NULL,
  id_user int(15) NOT NULL,
  status varchar(25) NOT NULL default 'OK',
  description varchar(255) default NULL,
  PRIMARY KEY (id),
  KEY (id_user),
  KEY (status)
) ENGINE=MyISAM;""")
