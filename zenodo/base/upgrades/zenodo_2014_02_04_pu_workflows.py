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
from sqlalchemy.sql import table, column, select
from sqlalchemy import String
import cPickle
import base64

depends_on = ['openaire_2013_12_17_wrkflwobj_status_fix']


def transform_data(data):
    """ Get rid of CoolList and CoolDict - not so cool anymore, eh! """
    if isinstance(data, dict):
        return dict([(k, transform_data(v)) for k, v in data.items()])
    elif isinstance(data, list):
        return [transform_data(x) for x in data]
    else:
        return data


def info():
    return "BibWorkflow pu-branch upgrade"


def do_upgrade():
    import invenio
    import sys
    import types

    class CoolDict(dict):
        pass

    class CoolList(list):
        pass

    # Fake old non-existing module
    m = types.ModuleType('invenio.bibfield_utils')
    m.CoolDict = CoolDict
    m.CoolList = CoolList
    sys.modules['invenio.bibfield_utils'] = m
    invenio.bibfield_utils = m

    # Minimal table definitions
    bwlobject = table(
        'bwlOBJECT',
        column('id', db.Integer(primary_key=True)),
        column('extra_data', db.MutableDict.as_mutable(db.PickleType)),
        column('_extra_data', db.LargeBinary()),
        column('_data', db.LargeBinary()),
    )

    bwlworkflow = table(
        'bwlWORKFLOW',
        column('uuid', db.String(36)),
        column('extra_data', db.MutableDict.as_mutable(db.PickleType)),
        column('_extra_data', db.LargeBinary()),
    )

    bwlobjectlogging = table(
        'bwlOBJECTLOGGING',
        column('id_object', db.Integer()),
        column('id_bibworkflowobject', db.Integer()),
    )

    bwlworkflowlogging = table(
        'bwlWORKFLOWLOGGING',
        column('id_object', db.String()),
        column('id_workflow', db.String()),
    )

    conn = op.get_bind()

    # Object table
    op.add_column('bwlOBJECT', db.Column(
                  '_extra_data', db.LargeBinary(), nullable=False))

    query = select(columns=['id', 'extra_data', '_data'], from_obj=bwlobject)
    for r in conn.execute(query):
        # Decode and re-encode old value
        value = base64.b64encode(cPickle.dumps(cPickle.loads(r.extra_data)))
        # Ensure data value can be read
        data_value = base64.b64encode(cPickle.dumps(
            transform_data(cPickle.loads(base64.b64decode(r._data)))
        ))

        # Update value in table.
        op.execute(
            bwlobject.update().where(bwlobject.c.id == r.id).values(
                _extra_data=value,
                _data=data_value,
            )
        )

    op.drop_column('bwlOBJECT', u'extra_data')
    op.alter_column('bwlOBJECT', 'data_type',
                    existing_type=mysql.VARCHAR(length=50),
                    nullable=True)
    op.alter_column('bwlOBJECT', 'id_workflow',
                    existing_type=mysql.VARCHAR(length=36),
                    nullable=True)

    # Workflow table
    op.add_column('bwlWORKFLOW', db.Column(
        '_extra_data', db.LargeBinary(), nullable=False))
    query = select(columns=['uuid', 'extra_data'], from_obj=bwlworkflow)
    for r in conn.execute(query):
        # Decode and re-encode old value
        value = base64.b64encode(cPickle.dumps(cPickle.loads(r.extra_data)))
        # Update value in table.
        op.execute(
            bwlworkflow.update().where(bwlworkflow.c.uuid == r.uuid).values(
                _extra_data=value
            )
        )
    op.drop_column('bwlWORKFLOW', u'extra_data')

    # Object logging
    op.add_column('bwlOBJECTLOGGING', db.Column(
        'id_object', mysql.INTEGER(display_width=255), nullable=False))
    op.execute(
        bwlobjectlogging.update().values({
            bwlobjectlogging.c.id_object:
            bwlobjectlogging.c.id_bibworkflowobject
        })
    )
    op.drop_column('bwlOBJECTLOGGING', u'id_bibworkflowobject')
    op.drop_column('bwlOBJECTLOGGING', u'extra_data')
    op.drop_column('bwlOBJECTLOGGING', u'error_msg')

    # Workflow logging
    op.add_column('bwlWORKFLOWLOGGING', db.Column(
        'id_object', db.String(length=255), nullable=False))
    op.execute(
        bwlworkflowlogging.update().values({
            bwlworkflowlogging.c.id_object:
            bwlworkflowlogging.c.id_workflow
        })
    )
    op.drop_column('bwlWORKFLOWLOGGING', u'id_workflow')
    op.drop_column('bwlWORKFLOWLOGGING', u'extra_data')
    op.drop_column('bwlWORKFLOWLOGGING', u'error_msg')
