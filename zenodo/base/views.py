# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
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
from flask import Blueprint, render_template
from flask.ext.menu import register_menu
from flask.ext.breadcrumbs import register_breadcrumb
from invenio.base.i18n import _

blueprint = Blueprint(
    'zenodo_base',
    __name__,
    url_prefix="",
    # menubuilder=[
    #     # Top menu
    #     ('main.browse', _('Browse'), '', 2),
    #     ('main.browse.datasets', _('Datasets'), 'collection.datasets', 1),
    #     ('main.browse.images', _('Images'), 'collection.images', 2),
    #     ('main.browse.posters', _('Posters'), 'collection.posters', 3),
    #     ('main.browse.presentations', _('Presentations'),
    #         'collection.presentations', 4),
    #     ('main.browse.publications', _('Publications'),
    #         'collection.publications', 5),
    #     ('main.browse.software', _('Software'), 'collection.software', 6),
    #     ('main.browse.videos', _('Video/Audio'), 'collection.videos', 6),
    #     ('main.getstarted', _('Get started'), '', 4),

    #     ('main.getstarted.faq', _('FAQ'), 'zenodo_base.faq', 4),

    #     # Footer menu
    #     ('footermenu_left.about', _('About'), 'zenodo_base.about', 1),
    #     ('footermenu_left.contact', _('Contact'),
    #         'zenodo_base.contact', 2),
    #     ('footermenu_left.policies', _('Policies'),
    #         'zenodo_base.policies', 3),
    #     ('footermenu_right.features', _('Features'),
    #         'zenodo_base.features', 1),
    #     ('footermenu_right.faq', _('FAQ'),
    #         'zenodo_base.faq', 4),
    #     ('footermenu_right.api', _('API'), 'zenodo_base.api', 5),
    #     ('footermenu_bottom.terms', _('Terms of use'),
    #         'zenodo_base.terms', 1),
    #     ('footermenu_bottom.privacy_policy', _('Privacy policy'),
    #         'zenodo_base.privacy_policy', 2),
    #     ('footermenu_bottom.support', _('Support/Feedback'),
    #         'zenodo_base.contact', 3),
    # ],
    static_folder="static",
    template_folder="templates",
)


#@register_menu(blueprint, 'main.search', _('Search'), order=1)
#@register_breadcrumb(blueprint, '.', _('Home'))

#register_menu()()

#
# Static pages
#
@blueprint.route('/features', methods=['GET', ])
@register_menu(blueprint, 'main.getstarted.features', _('Features'), order=1)
@register_breadcrumb(blueprint, '.features', _("Features"))
def features():
    return render_template('zenodo/features.html')


@blueprint.route('/use-data', methods=['GET', ])
@register_breadcrumb(blueprint, '.use_data', _("Use data"))
def use_data():
    return render_template('zenodo/use-data.html')


@blueprint.route('/deposit-data', methods=['GET', ])
@register_breadcrumb(blueprint, '.deposit_data', _("Deposit data"))
def deposit_data():
    return render_template('zenodo/deposit-data.html')


@blueprint.route('/about', methods=['GET', ])
@register_breadcrumb(blueprint, '.about', _("About"))
def about():
    return render_template('zenodo/about.html')


@blueprint.route('/contact', methods=['GET', ])
@register_breadcrumb(blueprint, '.contact', _("Contact"))
def contact():
    return render_template('zenodo/contact.html')


@blueprint.route('/dev', methods=['GET', ])
@register_breadcrumb(blueprint, '.api', _("API"))
def api():
    return render_template('zenodo/api.html')


@blueprint.route('/faq', methods=['GET', ])
@register_breadcrumb(blueprint, '.faq', _("FAQ"))
def faq():
    return render_template('zenodo/faq.html')


@blueprint.route('/policies', methods=['GET', ])
@register_breadcrumb(blueprint, '.policies', _("Policies"))
def policies():
    return render_template('zenodo/policies.html')


@blueprint.route('/partners', methods=['GET', ])
@register_breadcrumb(blueprint, '.partners', _("Partners"))
def partners():
    return render_template('zenodo/partners.html')


@blueprint.route('/terms', methods=['GET', ])
@register_breadcrumb(blueprint, '.terms', _("Terms of use"))
def terms():
    return render_template('zenodo/terms.html')


@blueprint.route('/privacy-policy', methods=['GET', ])
@register_breadcrumb(blueprint, '.privacy_policy', _("Privacy policy"))
def privacy_policy():
    return render_template('zenodo/privacy-policy.html')


@blueprint.route('/support', methods=['GET', ])
@register_breadcrumb(blueprint, '.support', _("Support/Feedback"))
def support():
    return render_template('zenodo/support.html')
