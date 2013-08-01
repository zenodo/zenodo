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

from wtforms import Field
from invenio.webdeposit_field import WebDepositField
from wtforms.validators import Regexp, ValidationError
from invenio.webdeposit_field_widgets import ButtonWidget
import re

__all__ = ['ReserveDOIField']

def reserve_doi_validator(form, field):
    from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME
    # field_doi = field.data
    # pub = getattr(form, '_pub', None)

    # if pub:
    #     reserved_doi = pub._metadata.get("__doi__", None)
    #     if reserved_doi and reserved_doi != field_doi and field_doi.startswith("%s/" % CFG_DATACITE_DOI_PREFIX):
    #         raise ValidationError('You are not allowed to edit a pre-reserved DOI. Click the Pre-reserve DOI button to resolve the problem.')

    # elif field_doi.startswith("%s/" % CFG_DATACITE_DOI_PREFIX):
    #     raise ValidationError('The prefix %s is administered automatically by %s. Please leave the field empty or click the "Pre-reserve DOI"-button and we will assign you a DOI.' % (CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME))

    # if CFG_DATACITE_DOI_PREFIX != "10.5072" and field_doi.startswith("10.5072/"):
    #     raise ValidationError('The prefix 10.5072 is invalid. The prefix is only used for testing purposes, and no DOIs with this prefix are attached to any meaningful content.')


class ReserveDOIField(WebDepositField(key=None), Field):
    widget = ButtonWidget(icon='icon-barcode')

    def __init__(self, doi_field=None, **kwargs):
        self.doi_field = doi_field
        super(ReserveDOIField, self).__init__(**kwargs)


    # def post_process(self, form):
    #     if self.data
    #         form.doi.data = "TEST"

    #     self.errors =

    #     form.publication_type.flags.hidden = True
    #     self.messages = [('info','Please try')]
    #     self.messages_state = 'info'

    # def pre_validate(self, form=None):

    #     if self.data:
    #         self.data = "MYTEST"
    #     # if not already reserved:
    #         # reserve recid
    #         # generate doi
    #     # else:
    #         # if DOI not already equal to reserved:
    #             # set reserved doi
    #     return dict(state="", message="", fields={self.doi_field: self.data})
