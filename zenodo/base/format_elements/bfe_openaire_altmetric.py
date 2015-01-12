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


def format_element(bfo, badgetype='donut', popover='', details='', css_class='', no_script=False):
    altmetric_id = bfo.field('035__a')
    doi = bfo.field('0247_a')

    if altmetric_id and doi:
        if popover:
            popover = " data-badge-popover=\"%s\"" % popover
        if details:
            details = " data-badge-details=\"%s\"" % details
        if css_class:
            css_class = " %s" % css_class

        if no_script:
            return """<div class="altmetric-embed%s" data-badge-type="%s"%s%s data-doi="%s"></div>""" % (css_class, badgetype, popover, details, doi)
        else:
            return "<script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>" \
            "<div class='altmetric-embed%s' data-badge-type='%s'%s%s data-doi=\"%s\"></div>" % (css_class, badgetype, popover, details, doi)
    else:
        return ""


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
