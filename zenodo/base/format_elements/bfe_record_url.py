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

from invenio.config import CFG_SITE_RECORD, CFG_SITE_URL, CFG_SITE_SECURE_URL


def format_element(bfo, with_ln="yes", absolute="no", secure="no"):
    """
    Prints the record URL.

    @param with_ln: if "yes" include "ln" attribute in the URL
    """

    base = ''
    if absolute.lower() == "yes":
        if secure.lower() == "yes":
            base = CFG_SITE_SECURE_URL
        else:
            base = CFG_SITE_URL

    url = ("%s/%s/" % (base, CFG_SITE_RECORD)) + bfo.control_field('001')

    if with_ln.lower() == "yes":
        url += "?ln=" + bfo.lang

    return url
