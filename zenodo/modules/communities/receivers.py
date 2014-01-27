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

from flask import current_app
from flask.ext.cache import make_template_fragment_key


def invalidate_jinja2_cache(sender, collection=None, lang=None, **extra):
    """
    Invalidate collection cache
    """
    from invenio.ext.cache import cache
    if lang is None:
        lang = current_app.config['CFG_SITE_LANG']
    cache.delete(make_template_fragment_key(collection.name, vary_on=[lang]))


def pre_curation_reject_listener(sender, action=None, recid=None,
                                 pretend=None):
    """
    Pre-curation reject listener that will add 'spam' collection identifier
    if a record is rejected.
    """
    if sender.id == "zenodo" and action == "reject":
        # Overrides all other collections identifiers
        return {'correct': [], 'replace': ['SPAM']}
    else:
        return None


def post_curation_reject_listener(sender, action=None, recid=None, record=None,
                                  pretend=None):
    """
    Post-curation reject listener that will inactive an already minted
    DOI for a rejected record.
    """
    if sender.id == "zenodo" and action == "reject" and not pretend:
        from zenodo.modules.deposit.tasks import openaire_delete_doi
        openaire_delete_doi.delay(recid)
