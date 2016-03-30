# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import six
import os
import shutil
import tempfile
from datetime import date

import pytest
from elasticsearch.exceptions import RequestError
from flask_cli import ScriptInfo
from invenio_db import db as db_
from invenio_files_rest.models import Location
from invenio_search import current_search
from sqlalchemy_utils.functions import create_database, database_exists
from invenio_records.api import Record
from zenodo.modules.records.serializers.bibtex import Bibtex

from zenodo.factory import create_app
from uuid import UUID


@pytest.yield_fixture(scope='session', autouse=True)
def app(request):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()

    os.environ.update(
        APP_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
    )

    app = create_app(
        DEBUG_TB_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
        CFG_SITE_NAME="testserver",
    )

    with app.app_context():
        yield app

    shutil.rmtree(instance_path)


@pytest.yield_fixture(scope='session')
def script_info(app):
    """Ensure that the database schema is created."""
    yield ScriptInfo(create_app=lambda info: app)


@pytest.yield_fixture()
def db(app):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.yield_fixture()
def location(db):
    """File system location."""
    tmppath = tempfile.mkdtemp()

    loc = Location(
        name='testloc',
        uri=tmppath,
        default=True
    )
    db.session.add(loc)
    db.session.commit()

    yield loc

    shutil.rmtree(tmppath)


@pytest.yield_fixture(scope='session')
def es(app):
    """Provide elasticsearch access."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete())
        list(current_search.create())
    yield current_search
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture()
def bibtex_records(app, db):
    """Create some records for bibtex serializer."""
    test_record = dict(
        recid=12345,
        system_number={"system_number": 2, "recid": 3},
        system_control_number={
            "system_control_number": "4", "institute": "CERN"},
        doi="10.1234/foo.bar",
        oai={"oai": "oai:zenodo.org:1",
             "indicator": ["user-zenodo", "user-ecfunded"]},
        upload_type={'type': 'publication', 'subtype': 'book'},
        collections=[{'primary': "pri", "secondary": "secondary", }],
        publication_date=six.text_type(date(2014, 2, 27)),
        #  creation_date=datetime.now(),
        #  modification_date=datetime.now(),
        title="Test title",
        authors=[
            {'name': 'Doe, John', 'affiliation': 'CERN', 'orcid': '',
             'familyname': 'Doe', 'givennames': 'John'},
            {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '',
             'familyname': 'Smith', 'givennames': 'John'},
        ],
        description="Test Description",
        keywords=["kw1", "kw2", "kw3"],
        notes="notes",
        access_right="open",
        #  embargo_date=date(2014, 2, 27),
        license={'identifier': 'cc-by', 'url': 'http://zenodo.org',
                 'source': 'opendefinition.org',
                 'license': 'Creative Commons', },
        imprint={
            'place': "Staszkowka",
            'publisher': "Jol"
        },
        communities=["zenodo"],
        provisional_communities=["ecfunded"],
        grants=[
            {"title": "Grant Title", "identifier": "1234", },
            {"title": "Title Grant", "identifier": "4321", },
        ],
        # Test all schemes
        related_identifiers=[
            {"identifier": "10.1234/foo.bar",
                "scheme": "doi", "relation": "cites"},
            {"identifier": "1234.4321", "scheme":
                "arxiv", "relation": "cites"},
        ],
        meetings={
            'title': 'The 13th Biennial HITRAN Conference',
            'place': 'Harvard-Smithsonian Center for Astrophysics',
            'dates': '23-25 June, 2014',
            'acronym': 'HITRAN13',
            'session': 'VI',
            'session_part': '1',
        },
        altmetric_id="9876",
        preservation_score="100",
        references=[
            {'raw_reference': 'Doe, John et al (2012). Some title. ZENODO. '
             '10.5281/zenodo.12'},
            {'raw_reference': 'Smith, Jane et al (2012). Some title. ZENODO. '
             '10.5281/zenodo.34'},
        ],
        part_of={
            'title': 'Bum'
        },
        journal={
            'title': 'Bam',
            'issue': '2',
            'pages': '20',
            'volume': '20'
        },
        thesis_university='I guess improtant',
        url=[
            {'url': 'one'},
            {'url': 'two'}
        ]
    )
    test_bad_record = dict(
        recid='12345',
        #  creation_date=datetime.now(),
        #  modification_date=datetime.now(),
    )
    with app.app_context():
        r_good = Record.create(test_record,
                               UUID("24029cb9-f0f8-4b72-94a7-bdf746f9d075"))
        r_bad = Record.create(test_bad_record,
                              UUID("0281c22c-266a-499b-8446-e12eff2f79b8"))
    db.session.commit()
    record_good = Bibtex(r_good)
    record_bad = Bibtex(r_bad)
    record_empty = Bibtex({})
    yield (record_good, record_bad, record_empty, r_good)
