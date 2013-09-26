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

from wtforms import TextAreaField
from invenio.webdeposit_workflow_utils import JsonCookerMixinBuilder
from invenio.openaire_deposit_engine import get_favourite_keywords_for_user
from invenio.webuser_flask import current_user
from wtforms.compat import text_type

__all__ = ['KeywordsField']


def _kb_transform(val):
    ret = {}
    ret['value'] = val
    ret['label'] = val
    return ret


class KeywordsField(TextAreaField, JsonCookerMixinBuilder('keywords')):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-tags"></i>'
        super(KeywordsField, self).__init__(**kwargs)

    def _value(self):
        if not self.data:
            return ""
        if isinstance(self.data, list):
            text = "\n".join(self.data)
            if isinstance(text, unicode):
                return text
            else:
                return text_type(text.decode('utf8'))
        else:
            return text_type(self.data)

    def pre_validate(self, form):
        return dict(error=0, error_message='')

    def autocomplete(self, term, limit):
        uid = current_user.get_id()
        if not term:
            term = ''
        return map(_kb_transform, get_favourite_keywords_for_user(uid, None, term)[:limit])
