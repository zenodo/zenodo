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

"""Celery tasks for harvesting grants."""

import json

from flask import current_app

from invenio.celery import celery
from invenio.modules.knowledge.api import update_kb_mapping, add_kb_mapping, \
    get_kb_mappings
from .contrib.openaire import OpenAireClient


def update_kb(kb_name, data, key_fun, value_fun=lambda x: x, update=False):
    """Update a knowledge base from data."""
    # Memory greedy, but faster than many individual SQL queries.
    mappings = dict([
        (d['key'], d['value']) for d in get_kb_mappings(kb_name)
    ])

    for item in data:
        k = key_fun(item)
        v = json.dumps(value_fun(item))
        if k not in mappings:
            add_kb_mapping(kb_name, k, v)
        elif update and mappings[k] != v:
            update_kb_mapping(kb_name, k, k, v)


@celery.task
def harvest_openaire_grants():
    """Harvest grants from OpenAIRE and store in knowledge base."""
    # OAI-PMH harvester client
    client = OpenAireClient(
        current_app.config['GRANTS_OPENAIRE_OAIPMH_ENDPOINT']
    )
    kb_json = current_app.config['GRANTS_OPENAIRE_KB_JSON']

    # Update knowledge base.
    update_kb(
        kb_json,
        client.list_grants(),
        key_fun=lambda x: x['grant_agreement_number'],
    )
