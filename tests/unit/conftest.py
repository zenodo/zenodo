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

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import shutil
import sys
import tempfile
from copy import deepcopy
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from celery import Task
from celery.messaging import establish_connection
from click.testing import CliRunner
from flask import current_app as flask_current_app
from flask import url_for
from flask.cli import ScriptInfo
from flask_celeryext import create_celery_app
from flask_security import login_user
from fs.opener import opener
from helpers import bearer_auth
from invenio_access.models import ActionUsers
from invenio_accounts.testutils import create_test_user
from invenio_admin.permissions import action_admin_access
from invenio_app.config import set_rate_limit
from invenio_communities.models import Community
from invenio_db import db as db_
from invenio_deposit.permissions import \
    action_admin_access as deposit_admin_access
from invenio_deposit.scopes import write_scope
from invenio_files_rest.models import Bucket, Location, ObjectVersion
from invenio_github.models import Repository
from invenio_indexer.api import RecordIndexer
from invenio_oaiserver.models import OAISet
from invenio_oauth2server.models import Client, Token
from invenio_oauthclient.models import RemoteAccount
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.resolver import Resolver
from invenio_queues.proxies import current_queues
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from invenio_records_files.api import RecordsBuckets
from invenio_search import current_search, current_search_client
from invenio_sipstore import current_sipstore
from pkg_resources import resource_stream
from six import BytesIO, b
from sqlalchemy_utils.functions import create_database, database_exists

from zenodo.config import APP_DEFAULT_SECURE_HEADERS
from zenodo.factory import create_app
from zenodo.modules.deposit.api import ZenodoDeposit as Deposit
from zenodo.modules.deposit.minters import zenodo_deposit_minter
from zenodo.modules.deposit.scopes import extra_formats_scope
from zenodo.modules.fixtures.records import loadsipmetadatatypes
from zenodo.modules.github.cli import github
from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.records.models import AccessRight
from zenodo.modules.records.serializers.bibtex import Bibtex
from zenodo.modules.tokens.scopes import tokens_generate_scope


def wrap_rate_limit():
    """Wrap rate limiter function to avoid affecting other tests."""
    if flask_current_app.config.get('USE_FLASK_LIMITER'):
        return set_rate_limit()
    else:
        return "1000 per second"


@pytest.fixture
def use_flask_limiter(app):
    """Activate flask limiter."""
    flask_current_app.config.update(dict(
        USE_FLASK_LIMITER=True,
        RATELIMIT_GUEST_USER='2 per second',
        RATELIMIT_AUTHENTICATED_USER='4 per second',
        RATELIMIT_PER_ENDPOINT={
            'zenodo_frontpage.index': '10 per second',
            'security.login': '10 per second'
        }))
    yield
    flask_current_app.config['USE_FLASK_LIMITER'] = False


@pytest.yield_fixture(scope='session')
def instance_path():
    """Default instance path."""
    path = tempfile.mkdtemp()

    yield path

    shutil.rmtree(path)


@pytest.fixture(scope='module')
def script_dir(request):
    """Return the directory of the currently running test script."""
    return request.fspath.join('..')


@pytest.fixture(scope='session')
def env_config(instance_path):
    """Default instance path."""
    os.environ.update(
        INVENIO_INSTANCE_PATH=os.environ.get(
            'INSTANCE_PATH', instance_path),
        # To avoid rebuilding the assets during test time we provide our
        # prebuilt assets folder.
        INVENIO_STATIC_FOLDER=os.path.join(sys.prefix, 'var/instance/static')
    )

    return os.environ


@pytest.yield_fixture(scope='session')
def tmp_db_path():
    """Temporary database path."""
    os_path = tempfile.mkstemp(prefix='zenodo_test_', suffix='.db')[1]
    path = 'sqlite:///' + os_path
    yield path
    os.remove(os_path)


@pytest.fixture(scope='session')
def default_config(tmp_db_path):
    """Default configuration."""
    ZENODO_OPENAIRE_COMMUNITIES = {
        'foo': {
            'name': 'Foo Optimization Organization',
            'communities': ['c1', 'c2', ],
            'types': {
                'software': [
                    {'id': 'foo:t1', 'name': 'Foo sft type one'},
                    {'id': 'foo:t2', 'name': 'Foo sft type two'},
                ],
                'other': [
                    {'id': 'foo:t4', 'name': 'Foo other type four'},
                    {'id': 'foo:t5', 'name': 'Foo other type five'},
                ]
            }
        },
        'bar': {
            'name': 'Bar Association Resources',
            'communities': ['c3', 'c1'],
            'types': {
                'software': [
                    {'id': 'bar:t3', 'name': 'Bar sft type three'},
                ],
                'other': [
                    {'id': 'bar:t6', 'name': 'Bar other type six'},
                ]
            }
        }

    }

    # Disable HTTPS
    APP_DEFAULT_SECURE_HEADERS['force_https'] = False
    APP_DEFAULT_SECURE_HEADERS['session_cookie_secure'] = False

    return dict(
        RATELIMIT_APPLICATION=wrap_rate_limit,
        CFG_SITE_NAME="testserver",
        DEBUG_TB_ENABLED=False,
        APP_DEFAULT_SECURE_HEADERS=APP_DEFAULT_SECURE_HEADERS,
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        COMMUNITIES_MAIL_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
        LOGIN_DISABLED=False,
        DEPOSIT_DATACITE_MINTING_ENABLED=False,
        ZENODO_COMMUNITIES_AUTO_ENABLED=False,
        ZENODO_COMMUNITIES_AUTO_REQUEST=['zenodo', ],
        ZENODO_COMMUNITIES_NOTIFY_DISABLED=['zenodo', 'c2'],
        ZENODO_COMMUNITIES_ADD_IF_GRANTS=['grants_comm', ],
        ZENODO_COMMUNITIES_REQUEST_IF_GRANTS=['ecfunded', ],
        ZENODO_OPENAIRE_COMMUNITIES=ZENODO_OPENAIRE_COMMUNITIES,
        ZENODO_SITEMAP_MAX_URL_COUNT=20,
        SIPSTORE_ARCHIVER_WRITING_ENABLED=False,
        OAUTHLIB_INSECURE_TRANSPORT=True,
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', tmp_db_path),
        TESTING=True,
        THEME_SITEURL='http://localhost',
        WTF_CSRF_ENABLED=False,
        ZENODO_EXTRA_FORMATS_MIMETYPE_WHITELIST={
            'application/foo+xml': 'Test 1',
            'application/bar+xml': 'Test 2',
        },
        ZENODO_CUSTOM_METADATA_VOCABULARIES={
            'dwc': {
                '@context': 'http://rs.tdwg.org/dwc/terms/',
                'attributes': {
                    'family': {'type': 'keyword', },
                    'genus': {'type': 'keyword', },
                    'behavior': {'type': 'text', }
                }
            },
            'obo': {
                '@context': 'http://purl.obolibrary.org/obo/',
                'attributes': {
                    'RO_0002453': {'type': 'relationship', 'label': 'hostOf'},
                }
            },
        },
        SEARCH_INDEX_PREFIX='zenodo-test-',
    )


@pytest.yield_fixture(scope='session')
def app(env_config, default_config):
    """Flask application fixture."""
    app = create_app(**default_config)
    # FIXME: Needs fixing flask_celeryext,
    # which once creates the first celery app, the flask_app that is set
    # is never released from the global state, even if you create a new
    # celery application. We need to unset the "flask_app" manually.
    from celery import current_app as cca
    cca = cca._get_current_object()
    delattr(cca, "flask_app")
    celery_app = create_celery_app(app)

    # FIXME: When https://github.com/inveniosoftware/flask-celeryext/issues/35
    # is closed and Flask-CeleryExt is released, this can be removed.
    class _TestAppContextTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            if flask_current_app:
                return Task.__call__(self, *args, **kwargs)
            with self.app.flask_app.app_context():
                return Task.__call__(self, *args, **kwargs)

    celery_app.Task = _TestAppContextTask
    celery_app.set_current()

    with app.app_context():
        yield app


@pytest.fixture()
def api(app):
    """Flask application fixture."""
    return app.wsgi_app.mounts['/api']


@pytest.yield_fixture(scope='session')
def indexer_queue(app):
    """Bluk indexer celery queue."""
    queue = app.config['INDEXER_MQ_QUEUE']
    with establish_connection() as conn:
        q = queue(conn)
        yield q.declare()
        q.delete()


@pytest.yield_fixture()
def event_queues(app):
    """Delete and declare test queues."""
    current_queues.delete()
    try:
        current_queues.declare()
        yield current_queues.queues
    finally:
        current_queues.delete()


@pytest.yield_fixture
def communities_autoadd_enabled(app):
    """Temporarily enable auto-adding and auto-requesting of communities."""
    orig = app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']
    app.config['ZENODO_COMMUNITIES_AUTO_ENABLED'] = True
    yield app.config['ZENODO_COMMUNITIES_AUTO_ENABLED']
    app.config['ZENODO_COMMUNITIES_AUTO_ENABLED'] = orig


@pytest.yield_fixture
def communities_mail_enabled(app):
    """Temporarily enable auto-adding and auto-requesting of communities."""
    orig = app.config['COMMUNITIES_MAIL_ENABLED']
    app.config['COMMUNITIES_MAIL_ENABLED'] = True
    yield
    app.config['COMMUNITIES_MAIL_ENABLED'] = orig


@pytest.yield_fixture
def app_client(app):
    """Flask test client for UI app."""
    with app.test_client() as client:
        yield client


@pytest.yield_fixture
def api_client(api):
    """Flask test client for API app."""
    with api.test_client() as client:
        yield client


@pytest.fixture
def script_info(app):
    """Ensure that the database schema is created."""
    return ScriptInfo(create_app=lambda info: app)


@pytest.yield_fixture
def db(app):
    """Setup database."""
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()


@pytest.yield_fixture
def locations(db):
    """File system locations."""
    tmppath = tempfile.mkdtemp()
    arch_tmppath = tempfile.mkdtemp()

    loc = Location(
        name='testloc',
        uri=tmppath,
        default=True
    )

    arch_loc = Location(
        name='archive',
        uri=arch_tmppath,
        default=False
    )
    db.session.add(loc)
    db.session.add(arch_loc)
    db.session.commit()

    yield {'testloc': tmppath, 'archive': arch_tmppath}

    shutil.rmtree(tmppath)
    shutil.rmtree(arch_tmppath)
    # Delete the cached property value since the tmp archive changes
    current_sipstore.__dict__.pop('archive_location', None)


@pytest.fixture
def archive_fs(locations):
    """File system for the archive location."""
    archive_path = locations['archive']
    fs = opener.opendir(archive_path, writeable=False, create_dir=True)
    return fs


@pytest.yield_fixture
def es(app):
    """Provide elasticsearch access."""
    list(current_search.delete(ignore=[400, 404]))
    current_search_client.indices.delete(index='*')
    current_search_client.indices.delete_template('*')
    list(current_search.create())
    list(current_search.put_templates())
    current_search_client.indices.refresh()
    try:
        yield current_search_client
    finally:
        current_search_client.indices.delete(index='*')
        current_search_client.indices.delete_template('*')


@pytest.fixture
def users(app, db):
    """Create users."""
    user1 = create_test_user(email='info@zenodo.org', password='tester')
    user2 = create_test_user(email='test@zenodo.org', password='tester2')
    user_admin = create_test_user(email='admin@zenodo.org',
                                  password='admin')

    with db.session.begin_nested():
        # set admin permissions
        db.session.add(ActionUsers(action=action_admin_access.value,
                                   user=user_admin))
        db.session.add(ActionUsers(action=deposit_admin_access.value,
                                   user=user_admin))
    db.session.commit()

    return [
        {'email': user1.email, 'id': user1.id},
        {'email': user2.email, 'id': user2.id},
        {'email': user_admin.email, 'id': user_admin.id}
    ]


@pytest.fixture
def communities(db, users):
    """Create communities."""
    comm_data = [
        {'id': 'c1', 'user_id': users[1]['id']},
        {'id': 'c2', 'user_id': users[1]['id']},
        {'id': 'c3', 'user_id': users[0]['id']},
        {'id': 'c4', 'user_id': users[0]['id']},
        {'id': 'c5', 'user_id': users[1]['id']},
        {'id': 'zenodo', 'user_id': users[2]['id']},
        {'id': 'ecfunded', 'user_id': users[2]['id']},
        {'id': 'grants_comm', 'user_id': users[2]['id']},
    ]
    for c in comm_data:
        Community.create(c['id'], user_id=c['user_id'])
    db.session.commit()
    return comm_data


@pytest.fixture
def oaisets(db, communities):
    """Create custom OAISet objects.

    Those should be custom OAISet objects which are not community based.
    """
    oaisets_data = [
        {
            'spec': 'extra',
            'search_pattern': 'title:extra'
        },
        {
            'spec': 'user-extra',  # Looks like a community-based OAISet
            'search_pattern': 'title:foobar'  # but has a search_pattern
        },
    ]
    for oai_data in oaisets_data:
        obj = OAISet(**oai_data)
        db.session.add(obj)
        db.session.commit()
        oai_data['id'] = obj.id
    return oaisets_data


@pytest.fixture
def oauth2_client(app, db, users):
    """Create client."""
    with db.session.begin_nested():
        # create resource_owner -> client_1
        client_ = Client(
            client_id='client_test_u1c1',
            client_secret='client_test_u1c1',
            name='client_test_u1c1',
            description='',
            is_confidential=False,
            user_id=users[0]['id'],
            _redirect_uris='',
            _default_scopes='',
        )
        db.session.add(client_)
    db.session.commit()
    return client_.client_id


@pytest.fixture
def write_token(app, db, oauth2_client, users):
    """Create token."""
    with db.session.begin_nested():
        token_ = Token(
            client_id=oauth2_client,
            user_id=users[0]['id'],
            access_token='dev_access_2',
            refresh_token='dev_refresh_2',
            expires=datetime.utcnow() + timedelta(hours=10),
            is_personal=False,
            is_internal=True,
            _scopes=write_scope.id,
        )
        db.session.add(token_)
    db.session.commit()
    return dict(
        token=token_,
        auth_header=[
            ('Authorization', 'Bearer {0}'.format(token_.access_token)),
        ]
    )


@pytest.fixture
def extra_token(app, db, oauth2_client, users):
    """Create token."""
    with db.session.begin_nested():
        token_ = Token(
            client_id=oauth2_client,
            user_id=users[0]['id'],
            access_token='dev_access_2',
            refresh_token='dev_refresh_2',
            expires=datetime.utcnow() + timedelta(hours=10),
            is_personal=False,
            is_internal=True,
            _scopes=' '.join([extra_formats_scope.id, write_scope.id])
        )
        db.session.add(token_)
    db.session.commit()
    return dict(
        token=token_,
        auth_header=[
            ('Authorization', 'Bearer {0}'.format(token_.access_token)),
        ]
    )


@pytest.fixture
def rat_generate_token(app, db, oauth2_client, users):
    """Create token."""
    with db.session.begin_nested():
        token_ = Token(
            client_id=oauth2_client,
            user_id=users[0]['id'],
            access_token='rat_token',
            expires=datetime.utcnow() + timedelta(hours=10),
            is_personal=False,
            is_internal=True,
            _scopes=tokens_generate_scope.id,
        )
        db.session.add(token_)
    db.session.commit()
    return token_


@pytest.fixture
def minimal_record():
    """Minimal record."""
    return {
        "$schema": "http://zenodo.org/schemas/records/record-v1.0.0.json",
        "recid": 123,
        "doi": "10.5072/zenodo.123",
        "resource_type": {
            "type": "software",
        },
        "publication_date": datetime.utcnow().date().isoformat(),
        "title": "Test",
        "creators": [{"name": "Test"}],
        "description": "My description",
        "access_right": "open",
    }


@pytest.fixture
def minimal_deposit():
    """Minimal deposit."""
    return {
        'metadata': {
            'upload_type': 'presentation',
            'title': 'Test title',
            'creators': [
                {'name': 'Doe, John', 'affiliation': 'Atlantis'},
                {'name': 'Smith, Jane', 'affiliation': 'Atlantis'},
            ],
            'description': 'Test Description',
            'publication_date': '2013-05-08',
            'access_right': 'open'
        }
    }


@pytest.fixture
def minimal_record_model(db, minimal_record, sip_metadata_types, recid_pid):
    """Minimal record."""
    model = RecordMetadata(id=str(recid_pid.object_uuid))
    model.created = datetime.utcnow() - timedelta(days=1)
    model.updated = model.created + timedelta(days=1)
    model.version_id = 0
    rec = ZenodoRecord(minimal_record, model=model)

    db.session.commit()

    return rec


@pytest.fixture
def recid_pid(db):
    """PID for minimal record."""
    pid = PersistentIdentifier.create(
        pid_type='recid', pid_value='123', status='R', object_type='rec',
        object_uuid=uuid4())
    db.session.commit()
    return pid


@pytest.fixture
def oaiid_pid():
    """PID for OAI id."""
    return PersistentIdentifier(
        pid_type='oai', pid_value='oai:zenodo.org:123', status='R',
        object_type='rec', object_uuid=uuid4())


@pytest.fixture
def bucket(db, locations):
    """File system location."""
    b1 = Bucket.create()
    db.session.commit()
    return b1


@pytest.fixture
def test_object(db, bucket):
    """File system location."""
    data_bytes = b('test object')
    obj = ObjectVersion.create(
        bucket, 'test.txt', stream=BytesIO(data_bytes),
        size=len(data_bytes)
    )
    db.session.commit()

    return obj


@pytest.fixture
def depid_pid(db):
    """PID for minimal record."""
    pid = PersistentIdentifier.create(
        pid_type='depid', pid_value='321', status='R', object_type='rec',
        object_uuid=uuid4())

    db.session.commit()
    return pid


@pytest.fixture
def full_record():
    """Full record fixture."""
    record = dict(
        recid=12345,
        doi='10.1234/foo.bar',
        resource_type={'type': 'publication', 'subtype': 'book'},
        publication_date=date(2014, 2, 27).isoformat(),
        title='Test title',
        creators=[
            {'name': 'Doe, John', 'affiliation': 'CERN',
             'gnd': '170118215', 'orcid': '0000-0002-1694-233X',
             'familyname': 'Doe', 'givennames': 'John',
             },
            {'name': 'Doe, Jane', 'affiliation': 'CERN',
             'gnd': '', 'orcid': '0000-0002-1825-0097',
             'familyname': 'Doe', 'givennames': 'Jane',
             },
            {'name': 'Smith, John', 'affiliation': 'CERN',
             'gnd': '', 'orcid': '',
             'familyname': 'Smith', 'givennames': 'John',
             },
            {'name': 'Nowak, Jack', 'affiliation': 'CERN',
             'gnd': '170118215', 'orcid': '',
             'familyname': 'Nowak', 'givennames': 'Jack',
             },
        ],
        description='Test Description',
        keywords=['kw1', 'kw2', 'kw3'],
        subjects=[
            {'term': 'Astronomy',
             'identifier': 'http://id.loc.gov/authorities/subjects/sh85009003',
             'scheme': 'url',
             },
        ],
        notes='notes',
        language='eng',
        version='1.2.5',
        access_right='open',
        # embargo_date
        # access_conditions
        license={
            'id': 'CC-BY-4.0',
            'url': 'https://creativecommons.org/licenses/by/4.0/',
            'title': 'Creative Commons Attribution 4.0',
        },
        communities=['zenodo'],
        grants=[
            {'title': 'Grant Title', 'code': '1234', 'identifiers': {},
             'internal_id': '10.1234/foo::1234',
             'funder': {'name': 'EC', 'doi': '10.1234/foo'}},
            {'title': 'Title Grant', 'code': '4321', 'identifiers': {},
             'internal_id': '10.1234/foo::4321',
             'funder': {'name': 'EC', 'doi': '10.1234/foo'}},
        ],
        related_identifiers=[
            {'identifier': '10.1234/foo.bar',
                'scheme': 'doi', 'relation': 'cites'},
            {'identifier': '1234.4325', 'scheme':
                'arxiv', 'relation': 'isIdenticalTo'},
            {'identifier': '1234.4321', 'scheme':
                'arxiv', 'relation': 'cites'},
            {'identifier': '1234.4328', 'scheme':
                'arxiv', 'relation': 'references'},
            {'identifier': '10.1234/zenodo.4321', 'scheme':
                'doi', 'relation': 'isPartOf',
                'resource_type': {
                    'type': 'software'}},
            {'identifier': '10.1234/zenodo.1234', 'scheme':
                'doi', 'relation': 'hasPart',
                'resource_type': {
                    'type': 'publication',
                    'subtype': 'section'
                }},
        ],
        alternate_identifiers=[
            {'identifier': 'urn:lsid:ubio.org:namebank:11815',
             'scheme': 'lsid', },
            {'identifier': '2011ApJS..192...18K',
             'scheme': 'ads', },
            {'identifier': '0317-8471',
             'scheme': 'issn', },
            {'identifier': '10.1234/alternate.doi',
             'scheme': 'doi',
             'resource_type': {
                    'type': 'publication',
                    'subtype': 'section'
                }},
        ],
        contributors=[
            {'affiliation': 'CERN', 'name': 'Smith, Other', 'type': 'Other',
             'gnd': '', 'orcid': '0000-0002-1825-0097'},
            {'affiliation': '', 'name': 'Hansen, Viggo', 'type': 'Other',
             'gnd': '', 'orcid': ''},
            {'affiliation': 'CERN', 'name': 'Kowalski, Manager',
             'type': 'DataManager'},
        ],
        references=[
            {'raw_reference': 'Doe, John et al (2012). Some title. Zenodo. '
             '10.5281/zenodo.12'},
            {'raw_reference': 'Smith, Jane et al (2012). Some title. Zenodo. '
             '10.5281/zenodo.34'},
        ],
        journal={
            'issue': '2',
            'pages': '20',
            'volume': '20',
            'title': 'Bam',
            'year': '2014',
        },
        meeting={
            'title': 'The 13th Biennial HITRAN Conference',
            'place': 'Harvard-Smithsonian Center for Astrophysics',
            'dates': '23-25 June, 2014',
            'acronym': 'HITRAN13',
            'session': 'VI',
            'session_part': '1',
            'url': 'http://hitran.org/conferences/hitran-13-2014/'
        },
        imprint={
            'place': 'Staszkowka',
            'publisher': 'Jol',
            'isbn': '978-0201633610'
        },
        part_of={
            'title': 'Bum',
            'pages': '1-2',
        },
        thesis={
            'university': 'I guess important',
            'supervisors': [
                {'name': 'Smith, Professor'},
            ],
        },
        dates=[
            {'type': 'Valid', 'start': '2019-01-01', 'description': 'Bongo'},
            {'type': 'Collected', 'end': '2019-01-01'},
            {'type': 'Withdrawn', 'start': '2019-01-01', 'end': '2019-01-01'},
            {'type': 'Collected', 'start': '2019-01-01', 'end': '2019-02-01'},
        ],
        owners=[1, ],
        method='microscopic supersampling',
        locations=[{"lat": 2.35, "lon": 1.534, "place": "my place"},
                   {'place': 'New York'}],
        _oai={
            'id': 'oai:zenodo.org:1',
            'sets': ['user-zenodo', 'user-ecfunded'],
            'updated': '2016-01-01T12:00:00Z'
        },
        _deposit={
            'id': '1',
            'created_by': 1,
            'owners': [1, ],
            'pid': {
                'revision_id': 1,
                'type': 'recid',
                'value': '12345',
            },
            'status': 'published'
        },
        _buckets={
            'deposit': '11111111-1111-1111-1111-111111111111',
            'record': '22222222-2222-2222-2222-222222222222',
        },
        _files=[
            {
                'bucket': '22222222-2222-2222-2222-222222222222',
                'version_id': '11111111-1111-1111-1111-111111111111',
                'file_id': '22222222-3333-4444-5555-666666666666',
                'checksum': 'md5:11111111111111111111111111111111',
                'key': 'test',
                'size': 4,
                'type': 'txt',
            }
        ],
    )
    record['$schema'] = 'http://zenodo.org/schemas/records/record-v1.0.0.json'
    return record


@pytest.fixture
def custom_metadata():
    """Custom metadata dictionary."""
    return {
        'dwc:family': ['Felidae'],
        'dwc:genus': ['Felis'],
        'dwc:behavior': ['Plays with yarn, sleeps in cardboard box.'],
        'obo:RO_0002453': [
            {
                'subject': ['Cat', 'Felis catus'],
                'object': ['Ctenocephalides felis', 'Cat flea'],
            },
        ],
    }


@pytest.fixture
def record_with_bucket(db, full_record, bucket, sip_metadata_types):
    """Create a bucket."""
    record = ZenodoRecord.create(full_record)
    record['_buckets']['record'] = str(bucket.id)
    record['_files'][0]['bucket'] = str(bucket.id)
    record.commit()
    RecordsBuckets.create(bucket=bucket, record=record.model)
    pid = PersistentIdentifier.create(
        pid_type='recid', pid_value=12345, object_type='rec',
        object_uuid=record.id, status='R')
    db.session.commit()
    return pid, record


@pytest.fixture
def record_with_files_creation(db, record_with_bucket):
    """Creation of a full record with files in database."""
    pid, record = record_with_bucket
    filename = 'Test.pdf'
    record.files[filename] = BytesIO(b'v1')
    record.files[filename]['type'] = 'pdf'
    record.commit()
    db.session.commit()

    record_url = url_for('invenio_records_ui.recid', pid_value=pid.pid_value)

    return pid, record, record_url


@pytest.fixture
def record_with_image_creation(db, record_with_bucket):
    """Creation of a full record with files in database."""
    pid, record = record_with_bucket
    filename = 'Test.png'
    record.files[filename] = resource_stream(
        'zenodo.modules.theme', 'static/img/eu.png')
    record.files[filename]['type'] = 'png'
    record.commit()
    db.session.commit()

    record_url = url_for('invenio_records_ui.recid', pid_value=pid.pid_value)

    return pid, record, record_url


@pytest.fixture
def closed_access_record(db, es, record_with_files_creation):
    """Creation of a full record with closed access right."""
    _, record, record_url = record_with_files_creation
    record['access_right'] = AccessRight.CLOSED
    record.commit()
    db.session.commit()
    indexer = RecordIndexer()
    indexer.index(record)
    current_search.flush_and_refresh(index='records')
    return record


@pytest.fixture
def bibtex_records(app, db, full_record):
    """Create some records for bibtex serializer."""
    test_bad_record = dict(recid='12345')

    r_good = ZenodoRecord.create(
        full_record, UUID("24029cb9-f0f8-4b72-94a7-bdf746f9d075"))
    r_bad = ZenodoRecord.create(
        test_bad_record, UUID("0281c22c-266a-499b-8446-e12eff2f79b8"))
    db.session.commit()

    record_good = Bibtex(r_good)
    record_bad = Bibtex(r_bad)
    record_empty = Bibtex({})

    return (record_good, record_bad, record_empty, r_good)


@pytest.fixture
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


@pytest.fixture
def grant_records(db, es, funder_record):
    """Create grant records."""
    grants = [
        Record.create({
            '$schema': 'https://zenodo.org/schemas/grants/grant-v1.0.0.json',
            'internal_id': '10.13039/501100000780::282896',
            'funder': {'$ref': 'https://dx.doi.org/10.13039/501100000780'},
            'identifiers': {
                'eurepo': 'info:eu-repo/grantAgreement/EC/FP7/282896',
            },
            'code': '282896',
            'title': 'Open Access Research Infrastructure in Europe',
            'acronym': 'OpenAIREplus',
            'program': 'FP7',
        }),
        Record.create({
            '$schema': 'https://zenodo.org/schemas/grants/grant-v1.0.0.json',
            'internal_id': '10.13039/501100000780::027819',
            'funder': {'$ref': 'https://dx.doi.org/10.13039/501100000780'},
            'identifiers': {
                'eurepo': 'info:eu-repo/grantAgreement/EC/FP6/027819',
            },
            'code': '027819',
            'title': 'Integrating cognition, emotion and autonomy',
            'acronym': 'ICEA',
            'program': 'FP6',
        }),
    ]
    for g in grants:
        PersistentIdentifier.create(
            pid_type='grant', pid_value=g['internal_id'], object_type='rec',
            object_uuid=g.id, status='R')
    db.session.commit()
    for g in grants:
        RecordIndexer().index_by_id(g.id)
    current_search.flush_and_refresh(index='grants')
    return grants


@pytest.fixture
def license_record(db, es, sip_metadata_types):
    """Create a license record."""
    licenses = [
        Record.create({
            "$schema":
                "https://zenodo.org/schemas/licenses/license-v1.0.0.json",
            "domain_content": True,
            "domain_data": True,
            "domain_software": True,
            "family": "",
            "id": "CC-BY-4.0",
            "maintainer": "Creative Commons",
            "od_conformance": "approved",
            "osd_conformance": "not reviewed",
            "status": "active",
            "title": "Creative Commons Attribution International 4.0",
            "url": "https://creativecommons.org/licenses/by/4.0/"
        }),
        Record.create({
            "$schema":
                "https://zenodo.org/schemas/licenses/license-v1.0.0.json",
            "domain_content": True,
            "domain_data": True,
            "domain_software": True,
            "family": "",
            "id": "CC0-1.0",
            "maintainer": "Creative Commons",
            "od_conformance": "approved",
            "osd_conformance": "not reviewed",
            "status": "active",
            "title": "CC0 1.0",
            "url": "https://creativecommons.org/publicdomain/zero/1.0/"
        })
    ]
    for license in licenses:
        PersistentIdentifier.create(
            pid_type='od_lic', pid_value=license['id'], object_type='rec',
            object_uuid=license.id, status='R')

    db.session.commit()
    for license in licenses:
        RecordIndexer().index_by_id(license.id)
    current_search.flush_and_refresh(index='licenses')
    return licenses[1]


@pytest.fixture
def deposit_metadata():
    """Raw metadata of deposit."""
    data = dict(
        title='Test title',
        creators=[
            dict(name='Doe, John', affiliation='Atlantis'),
            dict(name='Smith, Jane', affiliation='Atlantis')
        ],
        description='Test Description',
        resource_type=dict(type='publication'),
        publication_date='2013-05-08',
        access_right='open'
    )
    return data


@pytest.fixture
def sip_metadata_types(db):
    """Create the SIP Metadata types."""
    loadsipmetadatatypes([
        {
            'title': 'Test Zenodo Record JSON v1.0.0',
            'name': 'json',
            'format': 'json',
            'schema': 'https://zenodo.org/schemas/records/record-v1.0.0.json'
        },
        {
            "title": "Test BagIt Archiver metadata",
            "name": "bagit",
            "format": "json",
            "schema": "https://zenodo.org/schemas/sipstore/bagit-v1.0.0.json"
        }
    ])


@pytest.fixture
def deposit(app, es, users, locations, deposit_metadata, sip_metadata_types):
    """New deposit with files."""
    with app.test_request_context():
        datastore = app.extensions['security'].datastore
        login_user(datastore.get_user(users[0]['email']))
        id_ = uuid4()
        zenodo_deposit_minter(id_, deposit_metadata)
        deposit = Deposit.create(deposit_metadata, id_=id_)
        db_.session.commit()
    current_search.flush_and_refresh(index='deposits')
    return deposit


@pytest.fixture
def deposit_file(deposit, db):
    """Deposit files."""
    deposit.files['test.txt'] = BytesIO(b'test')
    db.session.commit()
    return deposit.files


@pytest.fixture
def deposit_url(api):
    """Deposit API URL."""
    with api.test_request_context():
        return url_for('invenio_deposit_rest.depid_list')


@pytest.fixture
def json_headers():
    """JSON headers."""
    return [('Content-Type', 'application/json'),
            ('Accept', 'application/json')]


@pytest.fixture
def json_auth_headers(json_headers, write_token):
    """Authentication headers (with a valid oauth2 token).

    It uses the token associated with the first user.
    """
    return bearer_auth(json_headers, write_token)


@pytest.fixture
def auth_headers(write_token):
    """Authentication headers (with a valid oauth2 token).

    It uses the token associated with the first user.
    """
    return bearer_auth([], write_token)


@pytest.fixture
def extra_auth_headers(extra_token):
    """Authentication headers (with a valid oauth2 token).

    It uses the token associated with the first user.
    """
    return bearer_auth([], extra_token)


@pytest.fixture
def json_extra_auth_headers(json_headers, extra_token):
    """Authentication headers (with a valid oauth2 token).

    It uses the token associated with the first user.
    """
    return bearer_auth(json_headers, extra_token)


@pytest.fixture
def get_json():
    """Function for extracting json from response."""
    def inner(response, code=None):
        """Decode JSON from response."""
        data = response.get_data(as_text=True)
        if code is not None:
            assert response.status_code == code, data
        return json.loads(data)
    return inner


@pytest.yield_fixture
def legacyjson_v1():
    """Function for extracting json from response."""
    from zenodo.modules.records.serializers import legacyjson_v1 as serializer
    serializer.replace_refs = False
    yield serializer
    serializer.replace_refs = True


@pytest.fixture
def resolver():
    """Get a record resolver."""
    return Resolver(
        pid_type='recid', object_type='rec', getter=ZenodoRecord.get_record)


@pytest.fixture
def audit_records(minimal_record, db):
    """Audit test records."""
    records = {}
    for i in (1, 2, 3, 4):
        record = RecordMetadata()
        record.json = deepcopy(minimal_record)
        record.json['recid'] = i
        record.json['_oai'] = {
            'id': 'oai:{}'.format(i),
            'sets': [],
            'updated': datetime.utcnow().date().isoformat(),
        }

        db.session.add(record)
        db.session.commit()
        records[i] = str(ZenodoRecord(data=record.json, model=record).id)

        recid = PersistentIdentifier(pid_type='recid', pid_value=str(i),
                                     status='R', object_type='rec',
                                     object_uuid=record.id)
        oai_id = PersistentIdentifier(
            pid_type='oai', pid_value=record.json['_oai']['id'], status='R',
            object_type='rec', object_uuid=record.id)
        db.session.add(recid)
        db.session.add(oai_id)
        db.session.commit()
    return records


@pytest.fixture
def oaiset_update_records(minimal_record, db, es):
    """Fixture with records for query-based OAISet updating tests."""
    rec_ok = {
        'title': 'extra',
        '_oai': {
            'id': '12345',
            'sets': ['extra', 'user-foobar'],
            'updated': datetime(1970, 1, 1).isoformat(),
        }
    }
    # Record which needs removal of 'extra' from oai sets
    rec_remove = deepcopy(rec_ok)
    rec_remove['title'] = 'other'

    # Record which needs addition of 'extra' to oai sets
    rec_add = deepcopy(rec_ok)
    rec_add['_oai']['sets'] = ['user-foobar', ]
    records = [rec_ok, rec_remove, rec_add, ]

    rec_uuids = []
    for record_meta in records:
        rec = RecordMetadata()
        rec.json = deepcopy(record_meta)
        db.session.add(rec)
        db.session.commit()
        RecordIndexer().index_by_id(rec.id)
        rec_uuids.append(rec.id)
    current_search.flush_and_refresh('records')
    return rec_uuids


#
# GitHub-specific conftest
#
@pytest.fixture
def cli_run(app):
    """Fixture for CLI runner function.

    Returns a function accepting a single parameter (CLI command as string).
    """
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    def run(command):
        """Run the command from the CLI."""
        command_args = command.split()
        return runner.invoke(github, command_args, obj=script_info)
    yield run


@pytest.fixture
def g_users_data():
    """Data for users objects."""
    return [
        {'email': 'u1@foo.bar', 'password': '123456'},
        {'email': 'u2@foo.bar', 'password': '123456'},
    ]


@pytest.fixture
def g_users(app, db, g_users_data):
    """Fixture that contains multiple users for CLI/API tests."""
    datastore = app.extensions['security'].datastore
    for ud in g_users_data:
        user = datastore.create_user(**ud)
        db.session.commit()
        ud['id'] = user.id
    return g_users_data


@pytest.fixture
def g_remoteaccounts_data(g_users):
    """Data for RemoveAccount objects."""
    return [
        {
            'user_id': g_users[0]['id'],
            'extra_data': {
                'repos': {
                    '8000': {
                        'full_name': 'foo/bar',
                    },
                    '8002': {
                        'full_name': 'bacon/eggs',
                    },
                    '8003': {
                        'full_name': 'other/repo',
                    },
                }
            },
        }
    ]


@pytest.fixture
def g_remoteaccounts(app, db, g_remoteaccounts_data):
    """Fixture for RemoteAccount objects."""
    for rad in g_remoteaccounts_data:
        ra = RemoteAccount.create(rad['user_id'], 'changeme',
                                  rad['extra_data'])
        db.session.add(ra)
        db.session.commit()
        rad['id'] = ra.id
    return g_remoteaccounts_data


@pytest.fixture
def g_repositories_data(g_users):
    """Data for repositories."""
    return [
        {'name': 'foo/bar', 'github_id': 8000, 'user_id': g_users[0]['id']},
        {'name': 'baz/spam', 'github_id': 8001},
        {'name': 'bacon/eggs', 'github_id': 8002, 'user_id': g_users[0]['id']},
    ]


@pytest.fixture
def g_repositories(app, db, g_repositories_data):
    """Fixture for GitHub Repository objects."""
    for rd in g_repositories_data:
        repository = Repository(**rd)
        # We don't call GitHub hence the hook is not important, yet it should
        # be not null
        repository.hook = 12345
        db.session.add(repository)
        db.session.commit()
        rd['id'] = repository.id
    return g_repositories_data


@pytest.fixture
def g_tester_id(app, db):
    """Fixture that contains the test data for models tests."""
    datastore = app.extensions['security'].datastore
    tester = datastore.create_user(
        email='info@inveniosoftware.org', password='tester',
    )
    db.session.commit()
    return tester.id


@pytest.fixture
def sample_identifiers():
    """Sample of various identifiers."""
    return {
        'ads': ('ads:2011ApJS..192...18K',
                'https://ui.adsabs.harvard.edu/#abs/2011ApJS..192...18K'),
        'ark': ('ark:/13030/tqb3kh97gh8w', ''),
        'arxiv': ('hep-th/1601.07616',
                  'https://arxiv.org/abs/arXiv:1601.07616'),
        'bioproject': ('PRJNA224116',
                       'https://www.ebi.ac.uk/ena/data/view/PRJNA224116'),
        'biosample': ('SAMN08289383',
                      'https://www.ebi.ac.uk/ena/data/view/SAMN08289383'),
        'doi': ('10.1002/example',
                'https://doi.org/10.1002/example'),
        'ean13': ('4006381333931', ''),
        'ean8': ('73513537', ''),
        'ensembl': ('ENSMUST00000017290',
                    'https://www.ensembl.org/id/ENSMUST00000017290'),
        'genome': ('GCF_000001405.38',
                   'https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.38'),
        'gnd': ('4079154-3',
                'https://d-nb.info/gnd/4079154-3'),
        'hal': ('mem_13102590',
                'https://hal.archives-ouvertes.fr/mem_13102590'),
        'handle': ('10013/epic.10033',
                   'https://hdl.handle.net/10013/epic.10033'),
        'isbn': ('0-9752298-0-X', ''),
        'isni': ('1422-4586-3573-0476', ''),
        'issn': ('1188-1534', ''),
        'istc': ('0A9 2002 12B4A105 7', ''),
        'lsid': ('urn:lsid:ubio.org:namebank:11815', ''),
        'orcid': ('0000-0002-1694-233X',
                  'https://orcid.org/0000-0002-1694-233X'),
        'pmcid': ('PMC2631623',
                  'https://www.ncbi.nlm.nih.gov/pmc/PMC2631623'),
        'pmid': ('pmid:12082125',
                 'https://www.ncbi.nlm.nih.gov/pubmed/12082125'),
        'purl': ('http://purl.oclc.org/foo/bar',
                 'http://purl.oclc.org/foo/bar'),
        'refseq': ('NZ_JXSL01000036.1',
                   'https://www.ncbi.nlm.nih.gov/entrez/viewer.fcgi'
                   '?val=NZ_JXSL01000036.1'),
        'sra': ('SRR6437777',
                'https://www.ebi.ac.uk/ena/data/view/SRR6437777'),
        'uniprot': ('Q9GYV0',
                    'https://purl.uniprot.org/uniprot/Q9GYV0'),
        'url': ('http://www.heatflow.und.edu/index2.html',
                'http://www.heatflow.und.edu/index2.html'),
        'urn': ('urn:nbn:de:101:1-201102033592',
                'https://nbn-resolving.org/urn:nbn:de:101:1-201102033592'),
        'swh': ('swh:1:cnt:94a9ed024d3859793618152ea559a168bbcbb5e2',
                'https://archive.softwareheritage.org/'
                'swh:1:cnt:94a9ed024d3859793618152ea559a168bbcbb5e2'),
        'ascl': ('ascl:1908.011', 'https://ascl.net/1908.011'),
    }


@pytest.fixture
def mock_datacite_minting(mocker, app):
    """DOI registration enabled and DataCite calls mocked."""
    orig = app.config['DEPOSIT_DATACITE_MINTING_ENABLED']
    app.config['DEPOSIT_DATACITE_MINTING_ENABLED'] = True
    datacite_mock = mocker.patch(
        'invenio_pidstore.providers.datacite.DataCiteMDSClient')
    yield datacite_mock
    app.config['DEPOSIT_DATACITE_MINTING_ENABLED'] = orig
