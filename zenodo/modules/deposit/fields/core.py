# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from wtforms import TextAreaField
from wtforms.compat import text_type
from invenio.modules.deposit.field_base import WebDepositField


class TextAreaListField(WebDepositField, TextAreaField):
    def process_formdata(self, valuelist):
        self.data = []
        if valuelist and len(valuelist) > 0:
            for item in valuelist:
                for line in valuelist[0].splitlines():
                    if line.strip():
                        self.data.append(line.strip())

    def _value(self):
        return text_type("\n".join(self.data)) if self.data else ''


__all__ = ('TextAreaListField')
