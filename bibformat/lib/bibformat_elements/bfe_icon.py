# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
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

from jinja2 import Template
from invenio.bibdocfile import BibRecDocs
from invenio.config import CFG_SITE_URL
import re

template_icon = Template("""
<a href="/record/{{bfo.recID}}">
<img class="media-object img-rounded" width="90" src="{{icon.get_url()}}" />
</a>
""")
#<!-- BFE_OPENAIRE_ALTMETRIC badgetype='donut' popover='left' no_script='1'
# prefix="<br>" / -->


def format_element(bfo, template='record_hb.html', subformat_re='icon.*', **kwargs):
    bibarchive = BibRecDocs(bfo.recID)
    docs = bibarchive.list_bibdocs()
    if len(docs) > 0:
        doc = docs[0]
        icon = doc.get_icon(subformat_re=re.compile(subformat_re))
        if not icon:
            icon = doc.get_icon()
            if not icon:
                return ""

        else:
            ctx = {
                'icon': icon,
                'bfo': bfo,
                'CFG_SITE_URL': CFG_SITE_URL,
            }
            return template_icon.render(**ctx)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
