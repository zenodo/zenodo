# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

"""OpenAIRE Flask Blueprint"""
from flask import render_template
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint

blueprint = InvenioBlueprint('openaire', __name__,
  url_prefix="",
  #breadcrumbs=[(_('Comments'),
  #              'webcomment.subscribtions')],
  menubuilder=[
    ('main.submit', _('Submit'), 'deposit', 1),
    ('main.getstarted', _('Get started'), '', 2),
    ('main.getstarted.features', _('Features'), 'openaire.features', 1),
    ('main.getstarted.deposit_data', _('Deposit data'), 'openaire.deposit_data', 2),
    ('main.getstarted.use_data', _('Use data'), 'openaire.use_data', 3),
    ('main.getstarted.faq', _('FAQ'), 'openaire.faq', 4),
    ('footermenu_left.about', _('About'), 'openaire.about', 1),
    ('footermenu_left.contact', _('Contact'), 'openaire.contact', 2),
    ('footermenu_left.policies', _('Policies'), 'openaire.policies', 3),
    ('footermenu_left.partners', _('Partners'), 'openaire.partners', 4),
    ('footermenu_right.features', _('Features'), 'openaire.features', 1),
    ('footermenu_right.deposit_data', _('Deposit data'), 'openaire.deposit_data', 2),
    ('footermenu_right.use_data', _('Use data'), 'openaire.use_data', 3),
    ('footermenu_right.faq', _('FAQ'), 'openaire.faq', 4),
    ('footermenu_right.api', _('API'), 'openaire.api', 5),
    ('footermenu_bottom.terms', _('Terms of use'), 'openaire.terms', 1),
    ('footermenu_bottom.privacy_policy', _('Privacy policy'), 'openaire.privacy_policy', 2),
    ('footermenu_bottom.support', _('Support/Feedback'), 'openaire.support', 3),
    ]
)


@blueprint.route('/features', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Features"))
def features():
    return render_template('openaire_features.html')


@blueprint.route('/use-data', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Use data"))
def use_data():
    return render_template('openaire_use-data.html')


@blueprint.route('/deposit-data', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Deposit data"))
def deposit_data():
    return render_template('openaire_deposit-data.html')


@blueprint.route('/about', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("About"))
def about():
    return render_template('openaire_about.html')


@blueprint.route('/contact', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Contact"))
def contact():
    return render_template('openaire_contact.html')


@blueprint.route('/api', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("API"))
def api():
    return render_template('openaire_api.html')


@blueprint.route('/faq', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("FAQ"))
def faq():
    return render_template('openaire_faq.html')


@blueprint.route('/policies', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Policies"))
def policies():
    return render_template('openaire_policies.html')


@blueprint.route('/partners', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Partners"))
def partners():
    return render_template('openaire_partners.html')


@blueprint.route('/terms', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Terms of use"))
def terms():
    return render_template('openaire_terms.html')


@blueprint.route('/privacy-policy', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Privacy policy"))
def privacy_policy():
    return render_template('openaire_privacy-policy.html')


@blueprint.route('/support', methods=['GET', ])
@blueprint.invenio_set_breadcrumb(_("Support/Feedback"))
def support():
    return render_template('openaire_support.html')
