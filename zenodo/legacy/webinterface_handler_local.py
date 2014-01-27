# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
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
OpenAIRE local customization of Flask application
"""

import time
from invenio.config import CFG_SITE_LANG, CFG_WEBDEPOSIT_MAX_UPLOAD_SIZE
from invenio.textutils import nice_size
from invenio.signalutils import webcoll_after_webpage_cache_update
from invenio.modules.communities.signals import after_save_collection, \
    post_curation, pre_curation

from jinja2 import nodes
from jinja2.ext import Extension
from invenio.webuser_flask import current_user
from invenio.modules.communities.models import Community
from invenio.cache import cache
from invenio.search_engine import search_pattern_parenthesised



def customize_app(app):
    from flask import current_app

    app.config['MAX_CONTENT_LENGTH'] = CFG_WEBDEPOSIT_MAX_UPLOAD_SIZE

    #
    # Removed unwanted invenio menu items
    #
    del app.config['menubuilder_map']['main'].children['help']





    from invenio.restapi import setup_app
    setup_app(app)




def parse_filesize(s):
    """
    Convert a human readable filesize into number of bytes
    """
    sizes = [('', 1), ('kb', 1024), ('mb', 1024*1024), ('gb', 1024*1024*1024),
             ('g', 1024*1024*1024), ]
    s = s.lower()
    for size_str, val in sizes:
        intval = s.replace(size_str, '')
        try:
            return int(intval)*val
        except ValueError:
            pass
    raise ValueError("Could not parse '%s' into bytes" % s)


