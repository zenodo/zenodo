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
