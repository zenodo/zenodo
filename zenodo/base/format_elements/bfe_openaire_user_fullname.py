# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
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

import urllib

def format_element(bfo):
    """
    Prints the OpenAIRE user URL (used in OAI-PMH response).
    """
    name_encoded = urllib.quote_plus( bfo.field('8560_y').strip() )

    if name_encoded:
        return "info:openaire/surname/%s" % name_encoded
    else:
        return ""

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
