# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
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

"""Base blueprint for Zenodo."""

import copy
import time

import idutils

from flask import Blueprint, current_app, render_template, request
from flask.ext.breadcrumbs import register_breadcrumb
from flask.ext.login import current_user
from flask.ext.menu import current_menu, register_menu

from invenio.base.globals import cfg
from invenio.base.i18n import _
from invenio.base.signals import pre_template_render
from invenio.ext.template. \
    context_processor import register_template_context_processor


from zenodo.base.utils.bibtex import Bibtex
from zenodo.modules.accessrequests.models import SecretLink


blueprint = Blueprint(
    'zenodo_base',
    __name__,
    url_prefix="",
    static_folder="static",
    template_folder="templates",
)


@blueprint.before_app_first_request
def register_menu_items():
    """Setup menu for Zenodo."""
    item = current_menu.submenu('breadcrumbs.zenodo_base')
    item.register('', '')

    item = current_menu.submenu('main.browse')
    item.register(
        '', _('Browse'), order=3,
        active_when=lambda: request.endpoint.startswith("search.collection")
    )

    item = current_menu.submenu('main.browse.datasets')
    item.register(
        'search.collection', _('Datasets'), order=1,
        endpoint_arguments_constructor=lambda: dict(name='datasets')
    )

    item = current_menu.submenu('main.browse.images')
    item.register(
        'search.collection', _('Images'), order=2,
        endpoint_arguments_constructor=lambda: dict(name='images')
    )

    item = current_menu.submenu('main.browse.lessons')
    item.register(
        'search.collection', _('Lessons'), order=2,
        endpoint_arguments_constructor=lambda: dict(name='lessons')
    )

    item = current_menu.submenu('main.browse.posters')
    item.register(
        'search.collection', _('Posters'), order=3,
        endpoint_arguments_constructor=lambda: dict(name='posters')
    )

    item = current_menu.submenu('main.browse.presentations')
    item.register(
        'search.collection', _('Presentations'), order=4,
        endpoint_arguments_constructor=lambda: dict(name='presentations')
    )

    item = current_menu.submenu('main.browse.publications')
    item.register(
        'search.collection', _('Publications'), order=5,
        endpoint_arguments_constructor=lambda: dict(name='publications')
    )

    item = current_menu.submenu('main.browse.software')
    item.register(
        'search.collection', _('Software'), order=6,
        endpoint_arguments_constructor=lambda: dict(name='software')
    )

    item = current_menu.submenu('main.browse.videos')
    item.register(
        'search.collection', _('Video/Audio'), order=7,
        endpoint_arguments_constructor=lambda: dict(name='videos')
    )

    item = current_menu.submenu('main.getstarted')
    item.register(
        '', _('Get started'), order=5,
        active_when=lambda: request.endpoint.startswith("zenodo_base.")
    )

    def menu_fixup():
        # Change order
        item = current_menu.submenu("main.communities")
        item._order = 2

        # Change order and text
        item = current_menu.submenu("main.webdeposit")
        item._text = "Upload"
        item._order = 4

        item = current_menu.submenu("breadcrumbs.webdeposit")
        item._text = "Upload"

        # Remove items
        item = current_menu.submenu("main")
        item._child_entries.pop('documentation', None)

        item = current_menu.submenu("settings.groups")
        item.hide()
        item = current_menu.submenu("settings.workflows")
        item.hide()

        item = current_menu.submenu("main.getstarted.preservation")
        item.hide()

    # Append function to end of before first request functions, to ensure
    # all menu items have been loaded.
    current_app.before_first_request_funcs.append(menu_fixup)


def add_bibdoc_files(sender, **kwargs):
    """Add a variable 'zenodo_files' into record templates."""
    if 'recid' not in kwargs:
        return

    @register_template_context_processor
    def _add_bibdoc_files():
        from invenio.legacy.bibdocfile.api import BibRecDocs

        ctx = dict(
            zenodo_files=[f for f in BibRecDocs(
                kwargs['recid'], human_readable=True
            ).list_latest_files(
                list_hidden=False
            ) if not f.is_icon()],
            file_token=None,
        )

        token = request.args.get('token')
        if token:
            if SecretLink.validate_token(token,
                                         dict(recid=kwargs['recid'])):
                ctx["file_token"] = token
                return ctx
            else:
                pass  # Flash a message that token is invalid.

        ctx["zenodo_files"] = filter(
            lambda f: f.is_restricted(current_user)[0] == 0,
            ctx["zenodo_files"]
        )

        return ctx


@blueprint.before_app_first_request
def register_receivers():
    # Add template context processor to record request, that will add a files
    # variable into the template context
    pre_template_render.connect(add_bibdoc_files, 'record.metadata')
    pre_template_render.connect(add_bibdoc_files, 'record.files')
    pre_template_render.connect(add_bibdoc_files, 'record.usage')


#
# Template filters
#
@blueprint.app_template_filter('timefmt')
def timefmt_filter(value, format="%d %b %Y, %H:%M"):
    return time.strftime(format, value)


@blueprint.app_template_filter('bibtex')
def bibtex_filter(record):
    return Bibtex(record).format()


@blueprint.app_template_filter('is_local_doi')
def is_local_doi(value):
    """Convert DOI to a link."""
    if isinstance(value, basestring):
        return value.startswith(cfg['CFG_DATACITE_DOI_PREFIX']) or \
            value.startswith("10.5281/")
    return False


@blueprint.app_template_filter('is_record_owner')
def is_record_owner(bfo, tag="8560_f"):
    """Determine if current user is owner of a given record.

    @param bfo: BibFormat Object
    @param tag: Tag to use for extracting the email from the record.
    """
    email = bfo.field(tag)
    return email and current_user.is_active and \
        current_user['email'] == email


@blueprint.app_template_filter('zenodo_curated')
def zenodo_curated(reclist, length=10, reverse=False, open_only=False):
    """Show only curated publications from reclist."""
    from invenio.legacy.search_engine import search_pattern_parenthesised

    if open_only:
        p = "(collection:curated OR collection:user-zenodo) " \
            "AND (access_rights:open OR access_rights:embargoed)"
    else:
        p = "collection:curated OR collection:user-zenodo"

    reclist = (reclist & search_pattern_parenthesised(p=p))
    if reverse:
        reclist = reclist[-length:]
        return reversed(reclist)
    else:
        return reclist[:length]


RULES = {
    'f1000research': [{
        'prefix': '10.12688/f1000research',
        'relation': 'isCitedBy',
        'scheme': 'doi',
        'text': 'Published in',
        'image': 'img/f1000research.jpg',
        }],
    'inspire': [{
        'prefix': 'http://inspirehep.net/record/',
        'relation': 'isSupplementedBy',
        'scheme': 'url',
        'text': 'Available in',
        'image': 'img/inspirehep.png',
        }],
    'briefideas': [{
        'prefix': 'http://beta.briefideas.org/',
        'relation': 'isIdenticalTo',
        'scheme': 'url',
        'text': 'Published in',
        'image': 'img/briefideas.png',
        }],
    'zenodo': [{
        'prefix': 'https://github.com',
        'relation': 'isSupplementTo',
        'scheme': 'url',
        'text': 'Available in',
        'image': 'img/github.png',
        }, {
        'prefix': '10.1109/JBHI',
        'relation': 'isCitedBy',
        'scheme': 'doi',
        'text': 'Published in',
        'image': 'img/ieee.jpg',
        }],
}


@blueprint.app_template_filter('zenodo_related_links')
def zenodo_related_links(record):
    def apply_rule(item, rule):
        r = copy.deepcopy(rule)
        r['link'] = idutils.to_url(item['identifier'], item['scheme'])
        return r

    def match_rules(item, communities):
        rs = []
        for c in set(communities):
            if c in RULES:
                rules = RULES[c]
                for r in rules:
                    if item['relation'] == r['relation'] and \
                       item['scheme'] == r['scheme'] and \
                       item['identifier'].startswith(r['prefix']):
                        rs.append(r)
        return rs

    ret = []
    communities = record.get('communities', []) + \
        record.get('provisional_communities', [])
    for item in record.get('related_identifiers', []):
        for r in match_rules(item, communities):
            ret.append(apply_rule(item, r))

    return ret


@blueprint.app_template_filter('relation_title')
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
    elif relation == 'isNewVersionOf':
        return 'Previous versions'
    elif relation == 'isPreviousVersionOf':
        return 'New versions'
    return relation


@blueprint.app_template_filter('pid_url')
def pid_url(related_identifier):
    identifier = related_identifier.get('identifier')
    scheme = related_identifier.get('scheme')
    if scheme and identifier:
        return idutils.to_url(identifier, scheme)
    return ""


@blueprint.app_template_filter('schemaorg_type')
def schemaorg_type(recid=None, bfo=None):
    if recid:
        from invenio.modules.formatter.engine import BibFormatObject
        bfo = BibFormatObject(recid)

    if bfo:
        SCHEMAORG_MAP = current_app.config['SCHEMAORG_MAP']
        collections = bfo.fields('980__')
        for c in collections:
            a = c.get('a', None)
            b = c.get('b', None)
            res = SCHEMAORG_MAP.get(b if b else a, None)
            if res:
                return res
    return 'http://schema.org/CreativeWork'
