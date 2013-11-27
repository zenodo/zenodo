# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""Persistent Identifier Store administration interface"""


#from flask.ext.admin import expose
from invenio.adminutils import InvenioModelView
from invenio.sqlalchemyutils import db
from invenio.pidstore_model import PersistentIdentifier, PidLog


class PersistentIdentifierAdmin(InvenioModelView):
    _can_create = False
    _can_edit = False
    _can_delete = False

    #inline_models = [PidLog]

    column_list = ('type', 'pid', 'status', 'created', 'last_modified')
    column_searchable_list = ('pid',)
    column_choices = {
         'status': {
             'N': 'NEW',
             'R': 'REGISTERED',
             'K': 'RESERVED',
             'D': 'INACTIVE',
         }
    }
    page_size = 100

    def __init__(self, model, session, **kwargs):
        super(PersistentIdentifierAdmin, self).__init__(model, session, **kwargs)


class PidLogAdmin(InvenioModelView):
    _can_create = False
    _can_edit = False
    _can_delete = False

    column_list = ('id_pid', 'action', 'message')

    def __init__(self, model, session, **kwargs):
        super(PidLogAdmin, self).__init__(model, session, **kwargs)


def register_admin(app, admin):
    """
    Called on app initialization to register administration interface.
    """
    admin.add_view(PersistentIdentifierAdmin(PersistentIdentifier, db.session, name='Persistent identifiers', category="Persistent Identifiers"))
    admin.add_view(PidLogAdmin(PidLog, db.session, name='Log', category="Persistent Identifiers"))
