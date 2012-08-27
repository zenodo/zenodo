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
    """ Create table bibdocfsinfo """
    depends_on = ['baseline','0003_insert_notify_url_sbmfundesc']

    def forward(self):
        run_sql("""
CREATE TABLE IF NOT EXISTS bibdocfsinfo (
  id_bibdoc mediumint(9) unsigned NOT NULL,
  version tinyint(4) unsigned NOT NULL,
  format varchar(50) NOT NULL,
  last_version boolean NOT NULL,
  cd datetime NOT NULL,
  md datetime NOT NULL,
  checksum char(32) NOT NULL,
  filesize bigint(15) unsigned NOT NULL,
  mime varchar(100) NOT NULL,
  master_format varchar(50) NULL default NULL,
  PRIMARY KEY (id_bibdoc, version, format),
  KEY (last_version),
  KEY (format),
  KEY (cd),
  KEY (md),
  KEY (filesize),
  KEY (mime)
) ENGINE=MyISAM""")

