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
from invenio.legacy.dbquery import run_sql


depends_on = [u'zenodo_2014_03_18_schtask_fix']


def info():
    return "Fix hstRECORD and hstDOCUMENT"


def do_upgrade():
    run_sql("SET @rownum:=0; UPDATE hstRECORD SET id = @rownum:=@rownum+1")
    run_sql("ALTER TABLE `hstRECORD` ADD PRIMARY KEY(id, id_bibrec)")
    run_sql("ALTER TABLE `hstRECORD` CHANGE id id INTEGER(15) UNSIGNED NOT NULL AUTO_INCREMENT")

    run_sql("SET @rownum:=0; UPDATE hstDOCUMENT SET id = @rownum:=@rownum+1")
    run_sql("ALTER TABLE `hstDOCUMENT` ADD PRIMARY KEY(id, id_bibdoc)")
    run_sql("ALTER TABLE `hstDOCUMENT` CHANGE id id INTEGER(15) UNSIGNED NOT NULL AUTO_INCREMENT")


def estimate():
    return 1
