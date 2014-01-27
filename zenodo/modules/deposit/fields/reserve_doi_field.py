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

"""
Button that when clicked will reserve a DOI.
"""

from wtforms import Field
from invenio.modules.deposit.field_base import WebDepositField
from invenio.modules.deposit.processor_utils import replace_field_data
from invenio.modules.deposit.field_widgets import ButtonWidget


__all__ = ['ReserveDOIField']


def reserve_doi(dummy_form, field, submit=False, fields=None):
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
