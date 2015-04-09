# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""Button widget for WTForms."""

from wtforms.compat import text_type
from wtforms.widgets import HTMLString, html_params


class Button(object):

    """Simple HTML5 button widget with support for including an icon."""

    input_type = 'submit'

    def __init__(self, icon=None):
        """Initialize button."""
        self._icon = icon

    def __call__(self, field, **kwargs):
        """Render button."""
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('value', "y")
        return HTMLString('<button %s>%s%s</button>' % (
            html_params(name=field.name, **kwargs),
            "<i class=\"%s\"></i> " % self._icon if self._icon else "",
            text_type(field.label.text)
        ))
