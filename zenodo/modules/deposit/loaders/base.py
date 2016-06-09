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

from flask import request

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


def marshmallow_loader(schema_class):
    """Basic marshmallow loader generator."""
    def translator(data):
        result = schema_class().load(data)
        if result.errors:
            raise MarshmallowErrors(result.errors)
        return result.data
    return translator
