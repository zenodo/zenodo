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
from invenio.webdeposit_field import WebDepositField
from wtforms.compat import text_type
from wtforms.validators import Regexp, ValidationError
from invenio.textutils import wash_for_xml
import re


__all__ = ['RelatedIdentifiersField']

_RE_DOI = re.compile("(^$|(doi:)?10\.\d+(.\d+)*/.*)", flags=re.I)


def doi_list_validator(form, field):
    errors = []
    if isinstance(field.data, list):
        for doi in field.data:
            if not _RE_DOI.match(doi):
                errors.append(doi)
        if len(errors) > 2:
            s = "%s and %s" % (", ".join(errors[:-1]), errors[-1])
            raise ValidationError("The provided DOIs %s are invalid - they should look similar to '10.1234/foo.bar'." % s)
        elif len(errors) > 1:
            s = "%s and %s" % (errors[0], errors[1])
            raise ValidationError("The provided DOIs %s are invalid - they should look similar to '10.1234/foo.bar'." % s)
        elif len(errors) > 0:
            raise ValidationError("The provided DOI is invalid - it should look similar to '10.1234/foo.bar'.")


class RelatedIdentifiersField(WebDepositField, TextAreaField):
    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-barcode"></i>'
        kwargs['validators'] = [doi_list_validator]
        super(RelatedIdentifiersField, self).__init__(**kwargs)

    # def _value(self):
    #     if not self.data:
    #         return ""
    #     if isinstance(self.data, list):
    #         return text_type("\n".join(self.data))
    #     else:
    #         return text_type(self.data)
