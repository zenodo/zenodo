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

from __future__ import absolute_import, print_function, unicode_literals

import json
from datetime import datetime
from os.path import dirname, join

import arrow
from elasticsearch_dsl.utils import AttrDict
from flask import current_app
from flask_babelex import format_date, gettext
from invenio_search import current_search_client
from invenio_search.api import RecordsSearch
from jsonref import JsonRef
from speaklater import make_lazy_gettext

from .utils import is_valid_openaire_type

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

    _icon = {
        OPEN: 'fa-unlock',
        EMBARGOED: 'fa-ban',
        RESTRICTED: 'fa-key',
        CLOSED: 'fa-lock',
    }

    _description = {
        OPEN: _('Files are publicly accessible.'),
        EMBARGOED: _('Files are currently under embargo but will be publicly '
                     'accessible after {date}.'),
        RESTRICTED: _('You may request access to the files in this upload, '
                      'provided that you fulfil the conditions below. The '
                      'decision whether to grant/deny access is solely under '
                      'the responsibility of the record owner.'),
        CLOSED: _('Files are not publicly accessible.'),
    }

    _category = {
        OPEN: 'success',
        EMBARGOED: 'warning',
        RESTRICTED: 'danger',
        CLOSED: 'danger',
    }

    @staticmethod
    def is_embargoed(embargo_date):
        """Test if date is still under embargo."""
        return arrow.get(embargo_date).date() > datetime.utcnow().date()

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
    def as_icon(cls, value):
        """Get icon for a specific status."""
        return cls._icon[value]

    @classmethod
    def as_title(cls, value):
        """Get title for a specific status."""
        return dict(cls._all)[value]

    @classmethod
    def as_description(cls, value, embargo_date=None):
        """Get description for a specific status."""
        return cls._description[value].format(
            date=format_date(embargo_date, 'long'))

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
        endpoint = current_app.config['RECORDS_REST_ENDPOINTS']['recid']

        s = RecordsSearch(
            using=current_search_client,
            index=endpoint['search_index']
        ).query(
            'query_string',
            query='access_right:{0} AND embargo_date:{{* TO {1}}}'.format(
                cls.EMBARGOED,
                # Uses timestamp instead of date on purpose.
                datetime.utcnow().isoformat()
            ),
            allow_leading_wildcard=False
        ).source(False)

        return [hit.meta.id for hit in s.scan()]


class ObjectType(object):
    """Class to load object types data."""

    index_id = None
    index_internal_id = None
    types = None
    subtypes = None

    @classmethod
    def _load_data(cls):
        """Load object types for JSON data."""
        if cls.index_id is None:
            with open(join(dirname(__file__), "data", "objecttypes.json")) \
                    as fp:
                data = json.load(fp)

            cls.index_internal_id = {}
            cls.index_id = {}
            cls.types = set()
            cls.subtypes = {}
            for objtype in data:
                cls.index_internal_id[objtype['internal_id']] = objtype
                cls.index_id[objtype['id'][:-1]] = objtype
                if '-' in objtype['internal_id']:
                    type_, subtype = objtype['internal_id'].split('-')
                    cls.types.add(type_)
                    if type_ not in cls.subtypes:
                        cls.subtypes[type_] = set()
                    cls.subtypes[type_].add(subtype)
                else:
                    cls.types.add(objtype['internal_id'])

    @classmethod
    def validate_internal_id(cls, id):
        """Check if the provided ID corresponds to the internal ones."""
        cls._load_data()
        return id in cls.index_internal_id

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
    def get_types(cls):
        """Get object type value."""
        cls._load_data()
        return cls.types

    @classmethod
    def get_subtypes(cls, type_):
        """Get object type value."""
        cls._load_data()
        return cls.subtypes[type_]

    @classmethod
    def get_by_dict(cls, value):
        """Get object type dict with type and subtype key."""
        if not value:
            return None
        if 'subtype' in value:
            if isinstance(value, AttrDict):
                value = value.to_dict()
            internal_id = "{0}-{1}".format(
                value.get('type', ''),
                value.get('subtype', '')
            )
        else:
            internal_id = value['type']
        return cls.get(internal_id)

    @classmethod
    def get_openaire_subtype(cls, value):
        """Get the OpenAIRE community-specific subtype.

        OpenAIRE community-specific subtype requires that the record is
        accepted to the relevant community.

        :param value: Full 'metadata' dictionary. Higher level metadata is
                      required since we are fetching both 'resource_type' and
                      'communities'.
        :type value: dict
        :returns: Subtype in the form "openaire:<OA-comm-ID>:<OA-subtype-ID>"
                  or None.
        :rtype: str
        """
        comms = value.get('communities', [])
        oa_type = value['resource_type'].get('openaire_subtype')
        if oa_type and is_valid_openaire_type(value['resource_type'], comms):
            return 'openaire:' + oa_type


    @classmethod
    def get_cff_type(cls, value):
        resource_type_obj = cls.index_internal_id
        for key in resource_type_obj:
            if value == resource_type_obj[key].get('cff'):
                return resource_type_obj[key]['internal_id']
        return None
