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

#from fixture import DataSet
from invenio.base.factory import with_app_context


@with_app_context(new_context=True)
def post_handler_demosite_create(sender, default_data='', *args, **kwargs):
    """
    Loads data after demosite creation
    """
    from invenio.modules.communities.models import Community

    print(">>> Creating collections for communities...")
    c = Community.query.filter_by(id='zenodo').first()
    c.save_collections()

    c = Community.query.filter_by(id='ecfunded').first()
    c.save_collections()

    from invenio.modules.access.models import UserAccROLE
    from invenio.ext.sqlalchemy import db

    u = UserAccROLE(id_user=2, id_accROLE=17)
    db.session.add(u)
    db.session.commit()


@with_app_context(new_context=True)
def post_handler_demosite_populate(sender, default_data='', *args, **kwargs):
    """
    Loads data after records are created.
    """
