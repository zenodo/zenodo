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

from invenio.usercollection_model import UserCollection

# def _list_validator():
#     def _inner(form, field):
#         if isinstance(field.data, list):
#             for item in field.data:
#                 val = UserCollection.query.get(item)
#                 if val is None:
#                     raise ("%s is not a valid identifier.")
#     return _inner

def usercollection_autocomplete(dummy_form, dummy_field, term, limit=50):
    if not term:
        objs = UserCollection.query.limit(limit).all()
    else:
        term = '%' + term + '%'
        objs = UserCollection.query.filter(
            UserCollection.title.like(term) | UserCollection.id.like(term),
            UserCollection.id != 'zenodo'
        ).filter_by().limit(limit).all()

    return map(
        lambda o: {
            'value': o.title,
            'id': o.id,
            'curatedby': o.owner.nickname,
            'description': o.description,
        },
        objs
    )
