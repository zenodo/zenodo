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
from wtforms.validators import Required
from invenio.bibknowledge import get_kb_mappings
from invenio.webdeposit_field import WebDepositField

__all__ = ['JournalField']


def _kb_transform(val):
    ret = {}
    ret['value'] = val['key']
    ret['label'] = val['key']
    return ret


class JournalField(WebDepositField(key=None), TextField):

    def __init__(self, **kwargs):
        self._icon_html = ''

        # Create our own Required data member
        # for client-side use
        if 'validators' in kwargs:
            for v in kwargs.get("validators"):
                if type(v) is Required:
                    self.required = True

        super(JournalField, self).__init__(**kwargs)

    def pre_validate(self, form):
        return dict(error=0, error_message='')

    def autocomplete(self, term, limit):
        if not term:
            term = ''
        return map(_kb_transform, get_kb_mappings('journal_name', '', term)[:limit])
