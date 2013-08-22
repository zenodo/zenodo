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

"""
Button that when clicked will reserve a DOI.
"""

from wtforms import Field
from invenio.webdeposit_field import WebDepositField
from invenio.webdeposit_processor_utils import replace_field_data
from invenio.webdeposit_field_widgets import ButtonWidget


__all__ = ['ReserveDOIField']


def reserve_doi(dummy_form, field, dummy_submit):
    if field.object_data != field.data and field.data:
        if not field.object_data:
            # Call the user supplied function to create a doi.
            field.data = field.doi_creator()
        else:
            field.data = field.object_data


class ReserveDOIField(WebDepositField, Field):
    widget = ButtonWidget(icon='icon-barcode')

    def __init__(self, doi_field=None, doi_creator=None, **kwargs):
        self.doi_field = doi_field
        self.doi_creator = doi_creator
        defaults = dict(
            icon=None,
            processors=[
                reserve_doi,
                replace_field_data(
                    self.doi_field,
                    getter=lambda f: f.data['doi'] if isinstance(f.data, dict)
                    else f.data
                ),
            ],
        )
        defaults.update(kwargs)
        super(ReserveDOIField, self).__init__(**defaults)

    def _value(self):
        """
        Return true if button was pressed.
        """
        return bool(self.data)

    def process_formdata(self, valuelist):
        if self.object_data:
            # DOI already reserved, so set value to reserved DOI
            self.data = self.object_data
        elif (valuelist and valuelist[0] and (
              (isinstance(valuelist[0], basestring)
               and valuelist[0].lower() not in ['false', 'no']
               )
              or not (isinstance(valuelist[0], basestring)))
              ):
            self.data = True
