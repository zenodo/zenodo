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
def post_handler_database_create(sender, default_data='', *args, **kwargs):
    """
    Loads data after demosite creation
    """
    from invenio.modules.communities.models import Community

    print(">>> Creating collections for communities...")
    c = Community.query.filter_by(id='zenodo').first()
    c.save_collections()

    c = Community.query.filter_by(id='ecfunded').first()
    c.save_collections()

    print(">>> Fixing dbquery for root collection.")

    from invenio.modules.search.models import Collection
    from invenio.ext.sqlalchemy import db
    c = Collection.query.filter_by(id=1).first()
    c.dbquery = '980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT ' \
                '980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED ' \
                'AND NOT 980__a:DARK'
    db.session.commit()


@with_app_context(new_context=True)
def post_handler_demosite_populate(sender, default_data='', *args, **kwargs):
    """
    Loads data after records are created.
    """
