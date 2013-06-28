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

from wtforms import SelectField
from wtforms.validators import Required
from invenio.webdeposit_field import WebDepositField
from invenio.bibknowledge import get_kb_mappings
import json

__all__ = ['LicenseField']


def _kb_transform(val):
    val = json.loads(val['value'])
    val['value'] = val.get('title', '')
    return val


def _kb_license_choices(domain_data=True, domain_content=True, domain_software=True):
    def _mapper(x):
        license = json.loads(x['value'])
        if (license['domain_data'] and domain_data) or \
                (license['domain_content'] and domain_content) or \
                (license['domain_software'] and domain_software):
            return (x['key'], license['title'])
        else:
            return None
    return filter(lambda x: x is not None, map(_mapper, get_kb_mappings('licenses', '', '')))


class LicenseField(WebDepositField(key=None), SelectField):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-certificate"></i>'

        # Create our own Required data member
        # for client-side use
        if 'validators' in kwargs:
            for v in kwargs.get("validators"):
                if type(v) is Required:
                    self.required = True

        if 'choices' not in kwargs:
            license_filter = {}
            for opt in ['domain_data', 'domain_content', 'domain_software']:
                if opt in kwargs:
                    license_filter[opt] = kwargs[opt]
                    del kwargs[opt]
            kwargs['choices'] = _kb_license_choices(**license_filter)

        super(LicenseField, self).__init__(**kwargs)

    def pre_validate(self, form):
        return dict(error=0, error_message='')

    # def autocomplete(self, term, limit):
    #     if not term:
    #         term = ''
    #     return map(_kb_transform, get_kb_mappings('licenses', '', term)[:limit])
