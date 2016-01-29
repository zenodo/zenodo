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

"""Zenodo serializer tests."""

from __future__ import absolute_import, print_function

from dojson.contrib.to_marc21 import to_marc21
from invenio_pidstore.models import PersistentIdentifier
from invenio_records import Record
from marshmallow import Schema, fields

from zenodo.modules.records.serializers.marcxml import MARCXMLSerializer


class MySchema(Schema):
    """Test marshmallow schema."""

    control_number = fields.Str(attribute='pid.pid_value')


def test_serialize():
    """Test JSON serialize."""
    data = MARCXMLSerializer(to_marc21, schema_class=MySchema).serialize(
        PersistentIdentifier(pid_type='recid', pid_value='2'),
        Record({'title': 'test'}))
    assert data.decode('utf8') == \
        u'<collection xmlns="http://www.loc.gov/MARC21/slim">' \
        u'<record><controlfield tag="001">2</controlfield></record>' \
        u'</collection>'


def test_serialize_search():
    """Test JSON serialize."""
    def fetcher(obj_uuid, data):
        return PersistentIdentifier(pid_type='rec', pid_value=data['pid'])

    s = MARCXMLSerializer(to_marc21, schema_class=MySchema)
    data = s.serialize_search(
        fetcher,
        dict(
            hits=dict(
                hits=[
                    {'_source': dict(pid='1'), '_id': 'a', '_version': 1},
                    {'_source': dict(pid='2'), '_id': 'b', '_version': 1},
                ],
                total=2,
            ),
            aggregations={},
        )
    )
    assert data.decode('utf8') == \
        u'<collection xmlns="http://www.loc.gov/MARC21/slim">' \
        u'<record><controlfield tag="001">1</controlfield></record>' \
        u'<record><controlfield tag="001">2</controlfield></record>' \
        u'</collection>'
