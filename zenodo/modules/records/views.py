# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Blueprint for Zenodo-Records."""

from __future__ import absolute_import, print_function

import idutils
from flask import Blueprint, current_app

from .models import AccessRight, ObjectType

blueprint = Blueprint(
    'zenodo_records',
    __name__,
    template_folder='templates',
    url_prefix='/search'
)


#
# Access right template filters and tests.
#
@blueprint.app_template_test('accessright')
def is_valid_accessright(value):
    """Test if access right is valid."""
    return AccessRight.is_valid(value)


@blueprint.app_template_test('embargoed')
def is_embargoed(embargo_date, accessright=None):
    """Test if date is still embargoed (according to UTC date."""
    if accessright is not None and accessright != AccessRight.EMBARGOED:
        return False
    if embargo_date is not None:
        return AccessRight.is_embargoed(embargo_date)
    return False


@blueprint.app_template_filter()
def accessright_category(value, embargo_date=None):
    """Get category for access right."""
    return AccessRight.as_category(
        AccessRight.get(value, embargo_date=embargo_date))


@blueprint.app_template_filter()
def accessright_title(value, embargo_date=None):
    """Get category for access right."""
    return AccessRight.as_title(
        AccessRight.get(value, embargo_date=embargo_date))


#
# Object type template filters and tests.
#
@blueprint.app_template_filter()
def objecttype(value):
    """Get object type."""
    if not value:
        return None
    if 'subtype' in value:
        internal_id = "{0}-{1}".format(value['type'], value['subtype'])
    else:
        internal_id = value['type']
    return ObjectType.get(internal_id)


#
# Persistent identifiers template filters
#
@blueprint.app_template_test()
def local_doi(value):
    """Test if a DOI is a local DOI."""
    prefixes = current_app.config.get('ZENODO_LOCAL_DOI_PREFIXES', [])
    return prefixes and any((value.startswith(p + "/") for p in prefixes))


@blueprint.app_template_filter('relation_title')
def relation_title(relation):
    """Map relation type to title."""
    return dict(current_app.config['ZENODO_RELATION_TYPES']).get(relation) or \
        relation


@blueprint.app_template_filter('pid_url')
def pid_url(identifier, scheme=None):
    """Convert persistent identifier into a link."""
    if scheme is None:
        try:
            scheme = idutils.detect_identifier_schemes(identifier)[0]
        except IndexError:
            scheme = None
    if scheme and identifier:
        return idutils.to_url(identifier, scheme)
    return ""
