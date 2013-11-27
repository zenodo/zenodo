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

import time
from invenio.config import CFG_SITE_LANG, CFG_WEBDEPOSIT_MAX_UPLOAD_SIZE
from invenio.textutils import nice_size
from invenio.signalutils import webcoll_after_webpage_cache_update
from invenio.usercollection_signals import after_save_collection, \
    post_curation, pre_curation
from invenio.webdeposit_signals import template_context_created, file_uploaded
from invenio.webdeposit_local import index_context_listener
from jinja2 import nodes
from jinja2.ext import Extension
from invenio.webuser_flask import current_user
from invenio.usercollection_model import UserCollection
from invenio.cache import cache
from invenio.search_engine import search_pattern_parenthesised

JINJA_CACHE_ATTR_NAME = '_template_fragment_cache'
TEMPLATE_FRAGMENT_KEY_TEMPLATE = '_template_fragment_cache_%s%s'


def customize_app(app):
    from flask import current_app

    app.config['MAX_CONTENT_LENGTH'] = CFG_WEBDEPOSIT_MAX_UPLOAD_SIZE

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

    @app.template_filter('timefmt')
    def timefmt_filter(value, format="%d %b %Y, %H:%M"):
        return time.strftime(format, value)

    @app.template_filter('is_record_owner')
    def is_record_owner(bfo, tag="8560_f"):
        """
        Determine if current user is owner of a given record

        @param bfo: BibFormat Object
        @param tag: Tag to use for extracting the email from the record.
        """
        email = bfo.field(tag)
        return email and current_user.is_active and \
            current_user['email'] == email

    @app.template_filter('usercollection_id')
    def usercollection_id(coll):
        """
        Determine if current user is owner of a given record

        @param coll: Collection object
        """
        if coll:
            identifier = coll.name
            if identifier.startswith("provisional-user-"):
                return identifier[len("provisional-user-"):]
            elif identifier.startswith("user-"):
                return identifier[len("user-"):]
        return ""

    @app.template_filter('curation_action')
    def curation_action(recid, ucoll_id=None):
        """
        Determine if curation action is underway
        """
        return cache.get("usercoll_curate:%s_%s" % (ucoll_id, recid))

    @app.template_filter('zenodo_curated')
    def zenodo_curated(reclist, length=10, reverse=True, open_only=False):
        """
        Show only curated publications from reclist
        """
        if open_only:
            p = "(980__a:curated OR 980__a:user-zenodo) AND (542__l:open OR 542__l:embargoed)"
        else:
            p = "980__a:curated OR 980__a:user-zenodo"
        reclist = (reclist & search_pattern_parenthesised(p=p))
        if reverse:
            reclist = reclist[-length:]
            return reversed(reclist)
        else:
            return reclist[:length]

    @app.template_filter('usercollection_state')
    def usercollection_state(bfo, ucoll_id=None):
        """
        Determine if current user is owner of a given record

        @param coll: Collection object
        """
        coll_id_reject = "provisional-user-%s" % ucoll_id
        coll_id_accept = "user-%s" % ucoll_id

        for cid in bfo.fields('980__a'):
            if cid == coll_id_accept:
                return "accepted"
            elif cid == coll_id_reject:
                return "provisional"
        return "rejected"

    @app.template_filter('usercollections')
    def usercollections(bfo, is_owner=False, provisional=False, public=True, filter_zenodo=False):
        """
        Maps collection identifiers to community collection objects

        @param bfo: BibFormat Object
        @param is_owner: Set to true to only return user collections which the
                         current user owns.
        @oaram provisional: Return provisional collections (default to false)
        @oaram public: Return public collections (default to true)
        """
        colls = []
        if is_owner and current_user.is_guest:
            return colls

        for cid in bfo.fields('980__a'):
            # Remove zenodo collections from ab
            if filter_zenodo and (cid == 'user-zenodo' or
               cid == 'provisional-user-zenodo'):
                continue
            if provisional and cid.startswith('provisional-'):
                colls.append(cid[len("provisional-user-"):])
            elif public and cid.startswith('user-'):
                colls.append(cid[len("user-"):])

        query = [UserCollection.id.in_(colls)]
        if is_owner:
            query.append(UserCollection.id_user == current_user.get_id())

        return UserCollection.query.filter(*query).all()

    #
    # Removed unwanted invenio menu items
    #
    del app.config['menubuilder_map']['main'].children['help']

    # Add {% zenodocache tag %} and connect webcoll signal handler to invalidate
    # cache.
    app.jinja_env.add_extension(ZenodoExtension)

    webcoll_after_webpage_cache_update.connect(invalidate_jinja2_cache)
    after_save_collection.connect(invalidate_jinja2_cache)
    pre_curation.connect(pre_curation_reject_listener)
    post_curation.connect(post_curation_reject_listener)
    template_context_created.connect(
        index_context_listener,
        sender='webdeposit.index'
    )

    def large_file_notification(sender, deposition=None, deposition_file=None,
                                **kwargs):
        if deposition_file and deposition_file.size > 10485760:
            from invenio.mailutils import send_email
            from invenio.config import CFG_SITE_ADMIN_EMAIL, CFG_SITE_NAME
            from invenio.textutils import nice_size
            from invenio.jinja2utils import render_template_to_string
            current_app.logger.info(deposition_file.__getstate__())
            send_email(
                CFG_SITE_ADMIN_EMAIL,
                CFG_SITE_ADMIN_EMAIL,
                subject="%s: %s file uploaded" % (
                    CFG_SITE_NAME, nice_size(deposition_file.size)
                ),
                content=render_template_to_string(
                    "email_large_file.html",
                    deposition=deposition,
                    deposition_file=deposition_file,
                )
            )

    file_uploaded.connect(large_file_notification, weak=False)


    @app.template_filter('relation_title')
    def relation_title(relation):
        if relation == 'isCitedBy':
            return 'Cited by'
        elif relation == 'cites':
            return 'Cites'
        elif relation == 'isSupplementTo':
            return 'Supplement to'
        elif relation == 'isSupplementedBy':
            return 'Supplementary material'
        elif relation == 'references':
            return 'References'
        elif relation == 'isReferencedBy':
            return 'Referenced by'
        return relation

    @app.template_filter('pid_url')
    def pid_url(related_identifier):
        from invenio import pidutils
        identifier = related_identifier.get('identifier')
        scheme = related_identifier.get('scheme')
        if scheme and identifier:
            return pidutils.to_url(identifier, scheme)
        return ""

    @app.template_filter('schemaorg_type')
    def schemaorg_type(recid=None, bfo=None):
        if recid:
            from invenio.bibformat_engine import BibFormatObject
            bfo = BibFormatObject(recid)

        if bfo:
            from invenio.openaire_deposit_config import CFG_OPENAIRE_SCHEMAORG_MAP
            collections = bfo.fields('980__')
            for c in collections:
                a = c.get('a', None)
                b = c.get('b', None)
                res = CFG_OPENAIRE_SCHEMAORG_MAP.get(b if b else a, None)
                if res:
                    return res
        return 'http://schema.org/CreativeWork'

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


def make_template_fragment_key(fragment_name, vary_on=[]):
    """
    Make a cache key for a specific fragment name
    """
    if vary_on:
        fragment_name = "%s_" % fragment_name
    return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, "_".join(vary_on))


def invalidate_jinja2_cache(sender, collection=None, lang=None, **extra):
    """
    Invalidate collection cache
    """
    from invenio.cache import cache
    if lang is None:
        lang = CFG_SITE_LANG
    cache.delete(make_template_fragment_key(collection.name, vary_on=[lang]))


def pre_curation_reject_listener(sender, action=None, recid=None, pretend=None):
    """
    Pre-curation reject listener that will add 'spam' collection identifier
    if a record is rejected.
    """
    if sender.id == "zenodo" and action == "reject":
        # Overrides all other collections identifiers
        return {'correct': [], 'replace': ['SPAM']}
    else:
        return None


def post_curation_reject_listener(sender, action=None, recid=None, record=None, pretend=None):
    """
    Post-curation reject listener that will inactive an already minted
    DOI for a rejected record.
    """
    if sender.id == "zenodo" and action == "reject" and not pretend:
        from invenio.openaire_tasks import openaire_delete_doi
        openaire_delete_doi.delay(recid)


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
