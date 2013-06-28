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
from invenio.bibknowledge import get_kb_mappings, get_kb_mapping
import json


__all__ = ['FundingField']


def _kb_transform(val):
    data = json.loads(val.get('value', '{}'))
    data['label'] = "%s - %s (%s)" % (data['acronym'], data['title'], data['grant_agreement_number'])
    data['value'] = val['key']
    return data


def kb_list_validator(kb_name):
    def _inner(form, field):
        if isinstance(field.data, list):
            for item in field.data:
                val = get_kb_mapping(kb_name=kb_name, key=item, default=None)
                if val is None:
                    raise ("%s is not a valid grant agreement number.")
    return _inner


class FundingField(WebDepositField(key=None), TextField):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-money"></i>'

        # Create our own Required data member
        # for client-side use
        if 'validators' in kwargs:
            for v in kwargs.get("validators"):
                if type(v) is Required:
                    self.required = True

        kwargs['validators'] = [kb_list_validator("json_projects")]
        super(FundingField, self).__init__(**kwargs)

    def _value(self):
        # Input value field should be left blank, since values are displayed as
        # tags
        return ""

    def get_tags(self):
        if isinstance(self.data, list):
            projects = filter(
                lambda x: x is not None,
                map(
                    lambda x: _kb_transform(get_kb_mapping(kb_name="json_projects", key=x, default={})),
                    self.data
                )
            )
            return projects
        return []

    def autocomplete(self, term, limit):
        if not term:
            term = ''
        return map(_kb_transform, get_kb_mappings('json_projects', '', term)[:limit])
