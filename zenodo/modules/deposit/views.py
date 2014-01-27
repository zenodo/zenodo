# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
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

from __future__ import absolute_import

from flask import Blueprint
from invenio.modules.deposit.signals import template_context_created, \
    file_uploaded
from .receivers import index_context_listener, large_file_notification


blueprint = Blueprint(
    'zenodo_deposit',
    __name__,
    static_folder="static",
    template_folder="templates",
)


@blueprint.before_app_first_request
def register_receivers():
    """
    Setup signal receivers for deposit module.
    """
    template_context_created.connect(
        index_context_listener,
        sender='webdeposit.index'
    )

    file_uploaded.connect(large_file_notification, weak=False)
