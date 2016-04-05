# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""Helper models for Zenodo data model."""

from __future__ import absolute_import, print_function

import json
from datetime import datetime
from os.path import dirname, join

from flask import current_app
from flask_babelex import gettext
from invenio_search import Query, current_search_client
from jsonref import JsonRef
from speaklater import make_lazy_gettext

_ = make_lazy_gettext(lambda: gettext)


class AccessRight(object):
    """Class defining access right status."""

    OPEN = 'open'

    EMBARGOED = 'embargoed'

    RESTRICTED = 'restricted'

    CLOSED = 'closed'

    _all = (
        (OPEN, _('Open Access')),
        (EMBARGOED, _('Embargoed Access')),
        (RESTRICTED, _('Restricted Access')),
        (CLOSED, _('Closed Access')),
    )

    _category = {
        OPEN: 'success',
        EMBARGOED: 'warning',
        RESTRICTED: 'danger',
        CLOSED: 'danger',
    }

    @staticmethod
    def is_embargoed(embargo_date):
        """Test if date is still under embargo."""
        return embargo_date > datetime.utcnow().date()

    @classmethod
    def is_valid(cls, value):
        """Test if access right is valid."""
        return bool([key for key, title in cls._all if key == value])

    @classmethod
    def get(cls, value, embargo_date=None):
        """Get access right."""
        if embargo_date is not None and cls.EMBARGOED == value and \
           not cls.is_embargoed(embargo_date):
            return cls.OPEN

        return value

    @classmethod
    def as_title(cls, value):
        """Get title for a specific status."""
        return dict(cls._all)[value]

    @classmethod
    def as_category(cls, value, **kwargs):
        """Get title for a specific status."""
        cat = cls._category[value]
        return kwargs[cat] if cat in kwargs else cat

    @classmethod
    def as_options(cls):
        """Return list of access rights as options."""
        return cls._all

    @classmethod
    def get_expired_embargos(cls):
        """Get records for which the embargo period have expired."""
        query_str = 'access_right:{0} AND embargo_date:{{* TO {1}}}'.format(
            cls.EMBARGOED,
            datetime.utcnow().isoformat()
        )

        query = Query()
        query.body['query'] = {
            'query_string': {
                'query': query_str,
                'allow_leading_wildcard': False,
            }
        }

        endpoints = current_app.config['RECORDS_REST_ENDPOINTS']
        index = endpoints['recid']['search_index']

        response = current_search_client.search(
            index=index, body=query.body
        )
        return [hit['_id'] for hit in response['hits']['hits']]


class ObjectType(object):
    """Class to load object types data."""

    index_id = None
    index_internal_id = None

    @classmethod
    def _load_data(cls):
        """Load object types for JSON data."""
        if cls.index_id is None:
            with open(join(dirname(__file__), "data", "objecttypes.json")) \
                 as fp:
                data = json.load(fp)

            cls.index_internal_id = {}
            cls.index_id = {}
            for objtype in data:
                cls.index_internal_id[objtype['internal_id']] = objtype
                cls.index_id[objtype['id'][:-1]] = objtype

    @classmethod
    def _jsonloader(cls, uri, **dummy_kwargs):
        """Local JSON loader for JsonRef."""
        cls._load_data()
        return cls.index_id[uri]

    @classmethod
    def get(cls, value):
        """Get object type value."""
        cls._load_data()
        try:
            return JsonRef.replace_refs(
                cls.index_internal_id[value],
                jsonschema=True,
                loader=cls._jsonloader)
        except KeyError:
            return None

    @classmethod
    def get_by_dict(cls, value):
        """Get object type dict with type and subtype key."""
        if not value:
            return None
        if 'subtype' in value:
            internal_id = "{0}-{1}".format(value['type'], value['subtype'])
        else:
            internal_id = value['type']
        return cls.get(internal_id)
