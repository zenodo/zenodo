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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import tempfile
from datetime import date
from uuid import UUID, uuid4

import pytest
from elasticsearch.exceptions import RequestError
from flask_cli import ScriptInfo
from invenio_db import db as db_
from invenio_files_rest.models import Location
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_search import current_search, current_search_client
from sqlalchemy_utils.functions import create_database, database_exists

from zenodo.factory import create_app
from zenodo.modules.records.serializers.bibtex import Bibtex


@pytest.yield_fixture(scope='session', autouse=True)
def app():
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


@pytest.yield_fixture()
def es(app):
    """Provide elasticsearch access."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete())
        list(current_search.create())
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.fixture()
def minimal_record():
    """Minimal record."""
    return {
        "$schema": "http://zenodo.org/schemas/records/record-v1.0.0.json",
        "recid": 123,
        "resource_type": {
            "type": "software",
        },
        "publication_date": date.today().isoformat(),
        "title": "Test",
        "creators": [{"name": "Test"}],
        "description": "My description",
        "access_right": "open",
    }


@pytest.fixture()
def recid_pid():
    """PID for minimal record."""
    return PersistentIdentifier(
        pid_type='recid', pid_value='123', status='R', object_type='rec',
        object_uuid=uuid4())


@pytest.fixture()
def full_record():
    """Full record fixture."""
    record = dict(
        recid=12345,
        doi='10.1234/foo.bar',
        _oai={'id': 'oai:zenodo.org:1',
              'sets': ['user-zenodo', 'user-ecfunded']},
        resource_type={'type': 'publication', 'subtype': 'book'},
        publication_date=date(2014, 2, 27).isoformat(),
        title='Test title',
        creators=[
            {'name': 'Doe, John', 'affiliation': 'CERN', 'orcid': '',
             'familyname': 'Doe', 'givennames': 'John'},
            {'name': 'Smith, John', 'affiliation': 'CERN', 'orcid': '',
             'familyname': 'Smith', 'givennames': 'John'},
        ],
        description='Test Description',
        keywords=['kw1', 'kw2', 'kw3'],
        notes='notes',
        access_right='open',
        license={'identifier': 'cc-by', 'url': 'http://zenodo.org',
                 'source': 'opendefinition.org',
                 'license': 'Creative Commons', },
        imprint={
            'place': 'Staszkowka',
            'publisher': 'Jol'
        },
        communities=['zenodo'],
        provisional_communities=['ecfunded'],
        grants=[
            {'title': 'Grant Title', 'identifier': '1234', },
            {'title': 'Title Grant', 'identifier': '4321', },
        ],
        # Test all schemes
        related_identifiers=[
            {'identifier': '10.1234/foo.bar',
                'scheme': 'doi', 'relation': 'cites'},
            {'identifier': '1234.4321', 'scheme':
                'arxiv', 'relation': 'cites'},
        ],
        meetings=[{
            'title': 'The 13th Biennial HITRAN Conference',
            'place': 'Harvard-Smithsonian Center for Astrophysics',
            'dates': '23-25 June, 2014',
            'acronym': 'HITRAN13',
            'session': 'VI',
            'session_part': '1',
        }],
        altmetric_id='9876',
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
        thesis_university='I guess important',
    )
    record['$schema'] = 'http://zenodo.org/schemas/records/record-v1.0.0.json'
    return record


@pytest.yield_fixture()
def bibtex_records(app, db, full_record):
    """Create some records for bibtex serializer."""
    test_bad_record = dict(recid='12345')

    r_good = Record.create(
        full_record, UUID("24029cb9-f0f8-4b72-94a7-bdf746f9d075"))
    r_bad = Record.create(
        test_bad_record, UUID("0281c22c-266a-499b-8446-e12eff2f79b8"))
    db.session.commit()

    record_good = Bibtex(r_good)
    record_bad = Bibtex(r_bad)
    record_empty = Bibtex({})

    yield (record_good, record_bad, record_empty, r_good)


@pytest.fixture()
def funder_record(db):
    """Create a funder record."""
    funder = Record.create(dict(
        doi='10.13039/501100000780',
        name='European Commission',
        acronyms=['EC'],
    ))
    PersistentIdentifier.create(
        pid_type='frdoi', pid_value=funder['doi'], object_type='rec',
        object_uuid=funder.id, status='R')
    db.session.commit()
    return funder


@pytest.fixture()
def grant_record(db, funder_record):
    """Create a funder record."""
    grant = Record.create(dict(
        internal_id='10.13039/501100000780::282896',
        funder={'$ref': 'https://doi.org/10.13039/501100000780'},
        identifiers=dict(
            eurepo='info:eu-repo/grantAgreement/EC/FP7/282896',
        ),
        code='282896',
        title='Open Access Research Infrastructure in Europe',
        acronym='OpenAIREplus',
        program='FP7',
    ))
    PersistentIdentifier.create(
        pid_type='grant', pid_value=grant['internal_id'], object_type='rec',
        object_uuid=grant.id, status='R')
    db.session.commit()
    return grant
