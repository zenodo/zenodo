# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
Base blueprint for Zenodo
"""

import copy
import time
from flask import Blueprint, render_template, current_app
from flask.ext.menu import register_menu, current_menu
from flask.ext.breadcrumbs import register_breadcrumb
from flask.ext.login import current_user
from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.base.signals import pre_template_render
from invenio.ext.template.context_processor import \
    register_template_context_processor

from invenio.utils import persistentid

blueprint = Blueprint(
    'zenodo_base',
    __name__,
    url_prefix="",
    static_folder="static",
    template_folder="templates",
)


@blueprint.before_app_first_request
def register_menu_items():
    """
    Setup menu for Zenodo
    """
    item = current_menu.submenu('breadcrumbs.zenodo_base')
    item.register('', '')

    item = current_menu.submenu('main.browse')
    item.register('', _('Browse'), order=3)

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
    item.register('', _('Get started'), order=5)

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

    # Append function to end of before first request functions, to ensure
    # all menu items have been loaded.
    current_app.before_first_request_funcs.append(menu_fixup)


def add_bibdoc_files(sender, **kwargs):
    """
    Adds a variable 'zenodo_files' into record templates
    """
    if 'recid' not in kwargs:
        return

    @register_template_context_processor
    def _add_bibdoc_files():
        from invenio.legacy.bibdocfile.api import BibRecDocs
        return dict(
            zenodo_files=[f for f in BibRecDocs(
                kwargs['recid'], human_readable=True
            ).list_latest_files(
                list_hidden=False
            ) if not f.is_icon() and f.is_restricted(current_user)[0] == 0]
        )


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


@blueprint.app_template_filter('is_local_doi')
def is_local_doi(value):
    """ Convert DOI to a link. """
    return value.startswith(cfg['CFG_DATACITE_DOI_PREFIX']) or \
        value.startswith("10.5281/")


@blueprint.app_template_filter('is_record_owner')
def is_record_owner(bfo, tag="8560_f"):
    """
    Determine if current user is owner of a given record

    @param bfo: BibFormat Object
    @param tag: Tag to use for extracting the email from the record.
    """
    email = bfo.field(tag)
    return email and current_user.is_active and \
        current_user['email'] == email


@blueprint.app_template_filter('zenodo_curated')
def zenodo_curated(reclist, length=10, reverse=False, open_only=False):
    """
    Show only curated publications from reclist
    """
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
    'zenodo': [{
        'prefix': 'https://github.com',
        'relation': 'isSupplementTo',
        'scheme': 'url',
        'text': 'Available in',
        'image': 'img/github.png',
    }]
}


@blueprint.app_template_filter('zenodo_related_links')
def zenodo_related_links(record):
    def apply_rule(item, rule):
        r = copy.deepcopy(rule)
        r['link'] = persistentid.to_url(item['identifier'], item['scheme'])
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
        return persistentid.to_url(identifier, scheme)
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


#
# Static pages
#
@blueprint.route('/features', methods=['GET', ])
@register_menu(blueprint, 'main.getstarted.features', _('Features'), order=1)
@register_menu(blueprint, 'footermenu_right.features', _('Features'), order=1)
@register_breadcrumb(blueprint, 'breadcrumbs.features', _("Features"))
def features():
    return render_template('zenodo/features.html')


@blueprint.route('/use-data', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.use_data', _("Use data"))
def use_data():
    return render_template('zenodo/use-data.html')


@blueprint.route('/deposit-data', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.deposit_data', _("Deposit data"))
def deposit_data():
    return render_template('zenodo/deposit-data.html')


@blueprint.route('/about', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.about', _('About'), order=1)
@register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def about():
    return render_template('zenodo/about.html')


@blueprint.route('/contact', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.contact', _('Contact'), order=2)
@register_breadcrumb(blueprint, 'breadcrumbs.contact', _("Contact"))
def contact():
    return render_template('zenodo/contact.html')


@blueprint.route('/policies', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.policies', _('Policies'), order=3)
@register_breadcrumb(blueprint, 'breadcrumbs.policies', _("Policies"))
def policies():
    return render_template('zenodo/policies.html')


@blueprint.route('/dev', methods=['GET', ])
@register_menu(blueprint, 'footermenu_right.api', _('API'), order=5)
@register_breadcrumb(blueprint, 'breadcrumbs.api', _("API"))
def api():
    return render_template('zenodo/api.html')


@blueprint.route('/faq', methods=['GET', ])
@register_menu(blueprint, 'main.getstarted.faq', _('FAQ'), order=1)
@register_menu(blueprint, 'footermenu_right.faq', _('FAQ'), order=4)
@register_breadcrumb(blueprint, 'breadcrumbs.faq', _("FAQ"))
def faq():
    return render_template('zenodo/faq.html')


@blueprint.route('/terms', methods=['GET', ])
@register_menu(blueprint, 'footermenu_bottom.terms', _('Terms of use'),
               order=1)
@register_breadcrumb(blueprint, 'breadcrumbs.terms', _("Terms of use"))
def terms():
    return render_template('zenodo/terms.html')


@blueprint.route('/privacy-policy', methods=['GET', ])
@register_menu(blueprint, 'footermenu_bottom.privacy_policy',
               _('Privacy policy'), order=2)
@register_breadcrumb(blueprint, 'breadcrumbs.privacy_policy',
                     _("Privacy policy"))
def privacy_policy():
    return render_template('zenodo/privacy.html')


@blueprint.route('/support', methods=['GET', ])
@register_menu(blueprint, 'footermenu_bottom.support', _('Support/Feedback'),
               order=3)
@register_breadcrumb(blueprint, 'breadcrumbs.support', _("Support/Feedback"))
def support():
    return render_template('zenodo/contact.html')


@blueprint.route('/preservation-guidelines', methods=['GET', ])
@register_menu(blueprint, 'footermenu_left.preservation-guidelines', _('Preservation'), order=9)
@register_breadcrumb(blueprint, 'breadcrumbs.preservation-guidelines', _("Preservation guidelines"))
def preservation_guidelines():
    return render_template('zenodo/preservation-guidelines.html')
