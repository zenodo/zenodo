# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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

"""Zenodo base bundles."""

from invenio.base.bundles import styles as _s, jquery as _j, invenio as _i

#
# Site-wide JS
#
_i.contents += [
    "js/zenodo/init.js",
]

_j.contents += [
    "vendors/zeroclipboard/dist/ZeroClipboard.js",
    "vendors/bootstrap-datepicker/js/bootstrap-datepicker.js",
]

_j.bower.update({
    "zeroclipboard": "~2.1.6",
    "bootstrap-datepicker": "latest",
})

#
# Site-wide styles
#
_s.contents.remove("less/base.less")
_s.contents.remove("less/footer.less")
_s.contents += [
    "less/zenodo.less",
]
