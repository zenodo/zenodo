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
from invenio.signalutils import webcoll_after_webpage_cache_update
from jinja2 import nodes
from jinja2.ext import Extension

JINJA_CACHE_ATTR_NAME = '_template_fragment_cache'
TEMPLATE_FRAGMENT_KEY_TEMPLATE = '_template_fragment_cache_%s%s'


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

    @app.template_filter('filesizeformat')
    def filesizeformat_filter(value):
        """
        Jinja2 filesizeformat filters is broken in Jinja2 up to v2.7, so
        let's implement our own.
        """
        return nice_size(value)

    @app.template_filter('timefmt')
    def timefmt_filter(value, format="%d %b %Y, %H:%M"):
        import time
        return time.strftime(format, value)

    #
    # Removed unwanted invenio menu items
    #
    del app.config['menubuilder_map']['main'].children['help']

    # Add {% zenodocache tag %} and connect webcoll signal handler to invalidate
    # cache.
    app.jinja_env.add_extension(ZenodoExtension)
    webcoll_after_webpage_cache_update.connect(invalidate_jinja2_cache, app)


def make_template_fragment_key(fragment_name, vary_on=[]):
    """
    Make a cache key for a specific fragment name
    """
    if vary_on:
        fragment_name = "%s_" % fragment_name
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, "_".join(vary_on))


def invalidate_jinja2_cache(sender, collection=None, lang=None):
    """
    Invalidate collection cache
    """
    from invenio.cache import cache
    cache.delete(make_template_fragment_key(collection.name, vary_on=[lang]))


class ZenodoExtension(Extension):
    """
    Temporary extension (let's see how long it will stay ;-).

    This extension is made until a pull-request has been integrated in the
    main Flask-Cache branch, so that generated cache keys are stable and
    predictable instead of based on filename and line numbers.
    """

    tags = set(['zenodocache'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        # Parse timeout
        args = [parser.parse_expression()]

        # Parse fragment name
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())

        # Parse vary_on parameters
        vary_on = []
        while parser.stream.skip_if('comma'):
            vary_on.append(parser.parse_expression())

        if vary_on:
            args.append(nodes.List(vary_on))
        else:
            args.append(nodes.Const([]))

        body = parser.parse_statements(['name:endcache'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_cache', args),
                               [], [], body).set_lineno(lineno)

    def _cache(self, timeout, fragment_name, vary_on,  caller):
        try:
            cache = getattr(self.environment, JINJA_CACHE_ATTR_NAME)
        except AttributeError, e:
            raise e

        key = make_template_fragment_key(fragment_name, vary_on=vary_on)

        # Delete key if timeout is 'del'
        if timeout == "del":
            cache.delete(key)
            return caller()

        rv = cache.get(key)
        if rv is None:
            rv = caller()
            cache.set(key, rv, timeout)
        return rv
