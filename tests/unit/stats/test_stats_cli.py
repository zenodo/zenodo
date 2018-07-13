# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Unit tests CLI commands for statistics."""

from click.testing import CliRunner
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from zenodo.modules.stats.cli import import_events


def test_record_view_import(app, db, es, event_queues, full_record,
                            script_info, tmpdir):
    """Test record page view event import."""
    full_record['conceptrecid'] = '12344'
    full_record['conceptdoi'] = '10.1234/foo.concept'
    r = Record.create(full_record)

    PersistentIdentifier.create(
        'recid', '12345', object_type='rec', object_uuid=r.id,
        status=PIDStatus.REGISTERED)
    db.session.commit()

    csv_file = tmpdir.join('record-views.csv')
    csv_file.write(
        ',userAgent,ipAddress,url,serverTimePretty,timestamp,referrer\n'
        ',foo,137.138.36.206,https://zenodo.org/record/12345,,1367928000,\n')

    runner = CliRunner()
    res = runner.invoke(
        import_events, ['record-view', csv_file.dirname], obj=script_info)
    assert res.exit_code == 0
    events = list(event_queues['stats-record-view'].consume())
    assert len(events) == 1
    assert events[0] == {
        'communities': ['zenodo'],
        'owners': [1],
        'conceptdoi': '10.1234/foo.concept',
        'conceptrecid': '12344',
        'doi': '10.1234/foo.bar',
        'ip_address': '137.138.36.206',
        'recid': '12345',
        'record_id': str(r.id),
        'referrer': '',
        'resource_type': {'subtype': 'book', 'type': 'publication'},
        'access_right': 'open',
        'timestamp': '2013-05-07T12:00:00',
        'user_agent': 'foo',
        'user_id': None,
    }
