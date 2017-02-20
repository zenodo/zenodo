# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016, 2017 CERN.
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

"""Zenodo Serializers."""

from __future__ import absolute_import, print_function

from flask import current_app, json
from invenio_files_rest.models import ObjectVersion
from invenio_records_files.api import FilesIterator

from zenodo.modules.records.api import ZenodoFileObject


def files_responsify(schema_class, mimetype):
    """Create a deposit files JSON serializer.

    :param schema_class: Marshmallow schema class.
    :param mimetype: MIME type of response.
    """
    def view(obj=None, pid=None, record=None, status=None):
        schema = schema_class(
            context={'pid': pid},
            many=isinstance(obj, FilesIterator)
        )

        if isinstance(obj, ObjectVersion):
            obj = ZenodoFileObject(obj, {})

        return current_app.response_class(
            json.dumps(schema.dump(obj.dumps()).data),
            mimetype=mimetype,
            status=status
        )

    return view
