# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015-2019 CERN.
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

"""Jinja utilities for Invenio."""

from __future__ import absolute_import, print_function

import collections

from invenio_indexer.signals import before_record_index
from invenio_pidrelations.contrib.versioning import versioning_blueprint
from six import itervalues
from werkzeug.utils import cached_property

from zenodo.modules.records.models import ObjectType

from . import config
from .custom_metadata import CustomMetadataAPI
from .indexer import indexer_receiver
from .proxies import current_zenodo_records
from .utils import serialize_record, transform_record, is_date_within_delta
from .views import blueprint, record_jinja_context


class ZenodoRecords(object):
    """Zenodo records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    @cached_property
    def resource_types(self):
        """Create an object list with the available resource types."""
        resource_list = []
        for item in itervalues(ObjectType.index_id):
            internal_id = item['internal_id']
            parent = item.get('parent')
            if parent:
                resolved_parent = ObjectType.get(item['internal_id'])['parent']
                parent_type_title = resolved_parent['title']['en']
            elif item.get('children'):
                continue
            else:
                parent_type_title = ''
            resource_list.append({
                'type': parent_type_title,
                'title': item['title']['en'],
                'id': internal_id
            })
        resource_list.sort(key=lambda x: x['title'])
        return resource_list

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)

        # Register context processors
        app.context_processor(record_jinja_context)
        app.context_processor(
            lambda: dict(current_zenodo_records=current_zenodo_records))
        app.context_processor(
            lambda: dict(is_date_within_delta=is_date_within_delta))
        # Register blueprint
        app.register_blueprint(blueprint)
        # Add global record serializer template filter
        app.add_template_filter(serialize_record, 'serialize_record')
        app.add_template_filter(transform_record, 'transform_record')

        # Register versioning blueprint
        app.register_blueprint(versioning_blueprint)

        self.custom_metadata = CustomMetadataAPI(
            term_types=app.config.get('ZENODO_CUSTOM_METADATA_TERM_TYPES'),
            vocabularies=app.config.get('ZENODO_CUSTOM_METADATA_VOCABULARIES'),
        )

        before_record_index.connect(indexer_receiver, sender=app)
        app.extensions['zenodo-records'] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('ZENODO_'):
                app.config.setdefault(k, getattr(config, k))
