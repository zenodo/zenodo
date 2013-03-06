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
from invenio.openaire_deposit_engine import get_favourite_authorships_for_user
from invenio.webuser_flask import current_user
from wtforms.compat import text_type
from invenio.textutils import wash_for_xml
import re

__all__ = ['AuthorField']

_RE_AUTHOR_ROW = re.compile(u'^\w{2,}(\s+\w{2,})*\s*,\s*(\w{2,}|\w\.)(\s+\w{1,}|\s+\w\.)*\s*(:\s*\w{2,}.*)?$', re.U)

# def _check_names(field, metadata, ln, _, mandatory=True):
#     names = metadata.get(field, '')
#     names = names.decode('UTF8')
#     if mandatory and not names.strip():
#         return (field, 'error', [_('The field is a mandatory field but is currently empty')])
#     errors = []
#     warnings = []
#     for row in names.splitlines():
#         row = row.strip()
#         if row:
#             if not _RE_AUTHOR_ROW.match(row):
#                 if not ',' in row:
#                     errors.append(_("""<strong>"%(row)s"</strong> is missing a comma separating last name and first name. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
#                 else:
#                     errors.append(_("""<strong>"%(row)s"</strong> is not well-formatted. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
#             if not ':' in row:
#                 warnings.append(_("""You have not specified an affiliation for <strong>"%(row)s"</strong> but an affiliation is recommended. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
#                 if row.islower():
#                     warnings.append(_("""It seems that the name <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"row": escape(row.encode('UTF8'))})
#             else:
#                 name, affiliation = row.split(":", 1)
#                 if name.islower():
#                     warnings.append(_("""It seems that the name <strong>"%(name)s"</strong> in <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
#                 if affiliation.islower():
#                     warnings.append(_("""It seems that the affiliation <strong>"%(affiliation)s"</strong> in <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"affiliation": escape(affiliation.encode('UTF8')), "row": escape(row.encode('UTF8'))})
#                 if name.isupper():
#                     warnings.append(_("""It seems that the name <strong>"%(name)s"</strong> in <strong>"%(row)s"</strong> has been written all upper case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
#                 if ':' in affiliation:
#                     warnings.append(_("""Please ensure you only have one name per line.""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
#     if errors:
#         return (field, 'error', errors)
#     elif warnings:
#         return (field, 'warning', warnings)


class AuthorField(TextAreaField, JsonCookerMixinBuilder('author')):

    def __init__(self, **kwargs):
        self._icon_html = '<i class="icon-user"></i>'
        super(AuthorField, self).__init__(**kwargs)

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.
        :param valuelist: A list of strings to process.
        """
        if valuelist:
            if isinstance(valuelist[0], basestring):
                self.data = []
                for author_str in [author.strip() for author in valuelist[0].encode('utf8').splitlines() if author.strip()]:
                    if ':' in author_str:
                        name, affil = author_str.split(':', 1)
                        name = wash_for_xml(name.strip())
                        affil = wash_for_xml(affil.strip())
                    else:
                        name = wash_for_xml(author_str.strip())
                        affil = None
                    self.data.append((name, affil))
            else:
                self.data = valuelist[0]

    def _value(self):
        if self.data:
            if isinstance(self.data, list):
                return text_type("\n".join(["%s: %s" % (x[0], x[1]) for x in self.data]))
            else:
                return text_type(self.data)
        else:
            return ''

    def autocomplete(self, term, limit):
        uid = current_user.get_id()
        if not term:
            term = ''
        return get_favourite_authorships_for_user(uid, None, term)
