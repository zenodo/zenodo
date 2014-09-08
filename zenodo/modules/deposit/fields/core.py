# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
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

import six
from wtforms import TextAreaField
from wtforms.compat import text_type
from invenio.modules.deposit.field_base import WebDepositField


class TextAreaListField(WebDepositField, TextAreaField):
    def process_formdata(self, valuelist):
        self.data = []
        if valuelist and isinstance(valuelist[0], six.string_types):
            for line in valuelist[0].splitlines():
                if line.strip():
                    self.data.append(line.strip())

    def _value(self):
        return text_type("\n".join(self.data)) if self.data else ''


__all__ = ('TextAreaListField')
