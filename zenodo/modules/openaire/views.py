# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Blueprint for OpenAIRE."""

from __future__ import absolute_import, print_function

import copy
from operator import itemgetter

import idutils
import six
from flask import Blueprint, current_app, render_template, request
from flask_principal import ActionNeed

from .helpers import is_openaire_dataset, is_openaire_publication, \
    openaire_link

blueprint = Blueprint(
    'zenodo_openaire',
    __name__
)


@blueprint.app_template_filter('is_openaire_publication')
def is_publication(record):
    """Test if record is an OpenAIRE publication."""
    return is_openaire_publication(record)


@blueprint.app_template_filter('is_openaire_dataset')
def is_dataset(record):
    """Test if record is an OpenAIRE dataset."""
    return is_openaire_publication(record)


@blueprint.app_template_filter('openaire_link')
def link(record):
    """Generate an OpenAIRE link."""
    return openaire_link(record)
