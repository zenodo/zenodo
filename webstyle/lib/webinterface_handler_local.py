# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
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

"""
OpenAIRE local customization of Flask application
"""

from invenio.textutils import nice_size


def customize_app(app):
    #from invenio.webinterface_handler_flask_utils import _
    from flask import current_app

    @app.context_processor
    def local_processor():
        """
        This will add variables to the Jinja2 to context containing the footer
        menus.
        """
        left = filter(lambda x: x.display(),
            current_app.config['menubuilder_map']['footermenu_left'].children.values())
        right = filter(lambda x: x.display(),
            current_app.config['menubuilder_map']['footermenu_right'].children.values())
        bottom = filter(lambda x: x.display(),
            current_app.config['menubuilder_map']['footermenu_bottom'].children.values())

        return dict(footermenu_left=left, footermenu_right=right,
            footermenu_bottom=bottom)

    @app.template_filter('filesize')
    def filesize_filter(value):
        """
        Jinja2 filesizeformat filters is broken in Jinja2 up to v2.7, so
        let's implement our own.
        """
        return nice_size(value)

    #
    # Removed unwanted invenio menu items
    #
    del app.config['menubuilder_map']['main'].children['help']
    del app.config['menubuilder_map']['main'].children['personalize']
