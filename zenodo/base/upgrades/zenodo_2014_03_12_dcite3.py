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
from datetime import datetime

depends_on = [u'zenodo_2014_02_04_pu_webtag']


def info():
    return "Add DataCite 3 metadata schema"


def pre_ugprade():
    # Check if formats can be made.
    from invenio.modules.formatter.models import Format
    Format(
        code='dcite3',
        name='DataCite 3.0',
        description='DataCite XML Metadata Kernel 3.0',
        content_type='text/xml',
        visibility=0,
        last_updated=datetime.now(),
    )


def do_upgrade():
    from invenio.modules.formatter.models import Format
    f1 = Format(
        code='dcite3',
        name='DataCite 3.0',
        description='DataCite XML Metadata Kernel 3.0',
        content_type='text/xml',
        visibility=0,
        last_updated=datetime.now(),
    )

    f2 = Format(
        code='oaidc3',
        name='OAI DataCite 3.0',
        description='OAI DataCite XML Metadata Kernel 3.0',
        content_type='text/xml',
        visibility=0,
        last_updated=datetime.now(),
    )

    db.session.add(f1)
    db.session.add(f2)
    db.session.commit()


def estimate():
    return 1
