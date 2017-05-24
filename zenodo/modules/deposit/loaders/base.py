# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Loaders for records."""

from __future__ import absolute_import, print_function

from flask import current_app, has_request_context, request

from zenodo.modules.records.minters import doi_generator

from ..errors import MarshmallowErrors


def json_loader(pre_validator=None, post_validator=None, translator=None):
    """Basic JSON loader with translation and pre/post validation support."""
    def loader(data=None):
        data = data or request.json

        if pre_validator:
            pre_validator(data)
        if translator:
            data = translator(data)
        if post_validator:
            post_validator(data)

        return data
    return loader


def marshmallow_loader(schema_class, **kwargs):
    """Basic marshmallow loader generator."""
    def translator(data):
        # Replace refs when we are in request context.
        context = dict(replace_refs=has_request_context())

        # DOI validation context
        if request and request.view_args.get('pid_value'):
            managed_prefix = current_app.config['PIDSTORE_DATACITE_DOI_PREFIX']

            _, record = request.view_args.get('pid_value').data
            context['recid'] = record['recid']
            if record.has_minted_doi() or record.get('conceptdoi'):
                context['required_doi'] = record['doi']
            elif not record.is_published():
                context['allowed_dois'] = [doi_generator(record['recid'])]
            else:
                # Ensure we cannot change to e.g. empty string.
                context['doi_required'] = True

            context['managed_prefixes'] = [managed_prefix]
            context['banned_prefixes'] = \
                ['10.5072'] if managed_prefix != '10.5072' else []

        # Extra context
        context.update(kwargs)

        # Load data
        result = schema_class(context=context).load(data)
        if result.errors:
            raise MarshmallowErrors(result.errors)
        return result.data
    return translator
