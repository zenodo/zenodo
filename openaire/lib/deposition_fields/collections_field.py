# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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

from wtforms import TextField
from wtforms.validators import Required, ValidationError
from invenio.webdeposit_field import WebDepositField
import json
from invenio.usercollection_model import UserCollection


__all__ = ['CollectionsField']


def _transform(val):
    return {
        'label': val.title,
        'value': val.id,
        'curatedby': val.owner.nickname,
        'description': val.description,
    }


def _list_validator():
    def _inner(form, field):
        if isinstance(field.data, list):
            for item in field.data:
                val = UserCollection.query.get(item)
                if val is None:
                    raise ("%s is not a valid identifier.")
    return _inner


class CollectionsField(WebDepositField(key=None), TextField):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-th-list"></i>'

        # Create our own Required data member
        # for client-side use
        if 'validators' in kwargs:
            for v in kwargs.get("validators"):
                if type(v) is Required:
                    self.required = True

        kwargs['validators'] = [_list_validator()]
        super(CollectionsField, self).__init__(**kwargs)

    def _value(self):
        # Input value field should be left blank, since values are displayed as
        # tags
        return ""

    def get_tags(self):
        if isinstance(self.data, list):
            tags = filter(
                lambda x: x is not None,
                map(
                    lambda x: _transform(UserCollection.query.get(x)),
                    self.data
                )
            )
            return tags
        return []

    def autocomplete(self, term, limit):
        if not term:
            objs = UserCollection.query.limit(limit).all()
        else:
            term = '%' + term + '%'
            objs = UserCollection.query.filter(
                UserCollection.title.like(term) | UserCollection.id.like(term),
                UserCollection.id != 'zenodo'
            ).filter_by().limit(limit).all()
        return map(_transform, objs)
