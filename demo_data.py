import random
from datetime import datetime

from flask_security.utils import hash_password
from invenio_accounts.proxies import current_accounts
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_files_rest.models import Bucket
from invenio_records_files.models import RecordsBuckets
from invenio_oauthclient.models import UserIdentity
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidrelations.contrib.versioning import PIDVersioning

from zenodo.modules.records.api import ZenodoRecord

WORDS = [
    'dataset',
    'picture',
    'figure',
    'software',
    'important',
    '2022',
    'version',
    'scientific',
    'research'
]


def demo_user(email, name, github=False, orcid=False):
    username = name.lower().replace(' ', '')
    user = current_accounts.datastore.create_user(
        email=email, password=hash_password('123456'),
        profile={'full_name': name, 'username': username})
    current_accounts.datastore.commit()

    if github:
        user.external_identifiers.append(
            UserIdentity(id=username, method='github'))
    if github:
        user.external_identifiers.append(
            UserIdentity(id=username, method='orcid'))
    db.session.commit()
    return user


def demo_record(recid_value, owner):
    bucket = Bucket.create()
    record = ZenodoRecord.create({
        "$schema": "http://zenodo.org/schemas/records/record-v1.0.0.json",
        "conceptrecid": 'C' + str(recid_value),
        "recid": recid_value,
        "conceptdoi": "10.5072/zenodo.C{}".format(recid_value),
        "doi": "10.5072/zenodo.{}".format(recid_value),
        "resource_type": {
            "type": "software",
        },
        "publication_date": datetime.utcnow().date().isoformat(),
        "title": "Test {} {}".format(
            recid_value,
            ' '.join(random.sample(WORDS, random.randint(1, 5)))
        ),
        "creators": [{"name": "Test {}".format(recid_value)}],
        "description": "My description",
        "access_right": "open",
        "owners": [owner],
        "_buckets": {
            "record": str(bucket.id)
        },
        '_deposit': {
            'id': str(recid_value),
            'created_by': owner,
            'owners': [owner],
        },
    })
    record.commit()
    RecordsBuckets.create(record.model, bucket)
    conceptrecid = PersistentIdentifier.create(
        'recid', record['conceptrecid'], status='K')
    recid = PersistentIdentifier.create(
        pid_type='recid', pid_value=recid_value, object_type='rec',
        object_uuid=record.id, status='R')
    pv = PIDVersioning(parent=conceptrecid)
    pv.insert_draft_child(recid)
    conceptdoi = PersistentIdentifier.create(
        pid_type='doi', pid_value=record['conceptdoi'], object_type='rec',
        object_uuid=record.id, status='K')
    doi = PersistentIdentifier.create(
        pid_type='doi', pid_value=record['doi'], object_type='rec',
        object_uuid=record.id, status='K')
    return recid, record


def demo_data(num=100, start=0):
    indexer = RecordIndexer()
    record_ids = []
    for i in range(start, start + num):
        user = demo_user(
            'user{}@zenodo.org'.format(i), 'User {}'.format(i),
            github=random.choice([True, False]),
            orcid=random.choice([True, False]),
        )
        print("creating records for user", user)

        for r in range(random.randint(1, 10)):
            recid = user.id * 100 + r
            _, record = demo_record(recid, user.id)
            record_ids.append(str(record.id))
        db.session.commit()
    for r in record_ids:
        indexer.index_by_id(r)
