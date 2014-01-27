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

from flask import current_app
from jinja2 import Template
from invenio.legacy.bibdocfile.api import BibRecDocs
import re

template_icon = Template("""
<a href="/record/{{bfo.recID}}">
<img class="media-object img-rounded" width="90" src="{{icon.get_url().replace(CFG_SITE_URL,'')}}" />
</a>
""")
#<!-- BFE_OPENAIRE_ALTMETRIC badgetype='donut' popover='left' no_script='1'
# prefix="<br>" / -->


def format_element(bfo, template='record_hb.html', subformat_re='icon.*', as_url=False, **kwargs):
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
            if as_url:
                return icon.get_url()
            else:
                ctx = {
                    'icon': icon,
                    'bfo': bfo,
                    'CFG_SITE_URL': current_app.config['CFG_SITE_URL'],
                }
                return template_icon.render(**ctx)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
