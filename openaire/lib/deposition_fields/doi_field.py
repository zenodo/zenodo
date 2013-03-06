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
from wtforms.validators import Regexp
import re

__all__ = ['DOIField']

doi_validator = Regexp("(^$|(doi:)?10\.\d+(.\d+)*/.*)", flags=re.I, message="The provided DOI is invalid - it should look similar to '10.1234/foo.bar'.")


class DOIField(TextField):
    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-barcode"></i>'
        kwargs['validators'] = [doi_validator]
        super(DOIField, self).__init__(**kwargs)
