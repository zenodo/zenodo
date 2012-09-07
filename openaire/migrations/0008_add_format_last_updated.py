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

from invenio.inveniocfg_migrate import InvenioMigration, run_sql_ignore
from invenio.dbquery import run_sql

class Migration( InvenioMigration ):
    """ Add column format.last_updated """

    repository = 'invenio_oa'
    """ Repository name """

    depends_on = ['baseline']
    """ A migration must depend on at least one previous migration """

    def forward(self):
        run_sql("ALTER TABLE format ADD COLUMN last_updated datetime NOT NULL default '0000-00-00' AFTER visibility;")
