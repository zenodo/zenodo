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

"""Test Zenodo deposit REST API."""

from __future__ import absolute_import, print_function

import json

from flask import url_for
from mock import patch
from invenio_communities.models import Community
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search
from six import BytesIO

from zenodo.modules.deposit.tasks import datacite_register


@patch('invenio_pidstore.providers.datacite.DataCiteMDSClient')
def test_edit_flow(datacite_mock, api_client, db, es, location,
                   json_auth_headers, deposit_url, get_json, auth_headers,
                   json_headers, license_record, communities, resolver):
    """Test simple flow using REST API."""
    headers = json_auth_headers
    client = api_client

    test_data = dict(
        metadata=dict(
            upload_type='presentation',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
                dict(name='Smith, Jane', affiliation='Atlantis')
            ],
            description='Test Description',
            publication_date='2013-05-08',
            access_right='open',
            license='CC0-1.0',
            communities=[{'identifier': 'c1'}, {'identifier': 'c3'}],
        )
    )

    # Create deposit
    response = client.post(
        deposit_url, data=json.dumps(test_data), headers=headers)
    data = get_json(response, code=201)

    # Get identifier and links
    current_search.flush_and_refresh(index='deposits')
    links = data['links']

    # Upload 3 files
    for i in range(3):
        f = 'test{0}.txt'.format(i)
        response = client.post(
            links['files'],
            data=dict(file=(BytesIO(b'ctx'), f), name=f),
            headers=auth_headers,
        )
        assert response.status_code == 201, i

    # Update metadata
    newdata = dict(metadata=data['metadata'])
    newdata['metadata']['title'] = 'Updated title'
    resdata = get_json(client.put(
        links['self'], data=json.dumps(newdata), headers=headers
    ), code=200)

    # Publish deposition
    response = client.post(links['publish'], headers=auth_headers)
    data = get_json(response, code=202)
    record_id = data['record_id']

    assert PersistentIdentifier.query.filter_by(pid_type='depid').count() == 1
    recid_pid = PersistentIdentifier.query.filter_by(pid_type='recid').one()
    doi_pid = PersistentIdentifier.get(
        pid_type='doi', pid_value='10.5072/zenodo.1')
    assert doi_pid.status == PIDStatus.RESERVED
    # This task (datacite_register) would normally be executed asynchronously
    datacite_register(recid_pid.pid_value, recid_pid.object_uuid)
    assert doi_pid.status == PIDStatus.REGISTERED

    # Make sure it was registered properly in datacite
    assert datacite_mock().metadata_post.call_count == 1
    datacite_mock().doi_post.assert_called_once_with(
         '10.5072/zenodo.1', 'https://zenodo.org/record/1')

    # Does record exists?
    current_search.flush_and_refresh(index='records')

    preedit_data = get_json(client.get(
        url_for('invenio_records_rest.recid_item', pid_value=record_id),
        headers=json_headers,
    ), code=200)
    expected_doi = '10.5072/zenodo.{0}'.format(record_id)
    assert preedit_data['doi'] == expected_doi
    # - community c3 got auto-accepted (owned by deposit user)
    assert preedit_data['metadata']['communities'] == [{'identifier': 'c3'}]

    # Are files downloadable by everyone (open)?
    assert len(preedit_data['files']) == 3
    download_url = preedit_data['files'][0]['links']['download']
    assert client.get(download_url).status_code == 200

    # Edit record - can now be done immediately after.
    response = client.post(links['edit'], headers=auth_headers)
    assert response.status_code == 201

    # Edit - 2nd time is invalid.
    response = client.post(links['edit'], headers=auth_headers)
    assert response.status_code == 403  # FIXME 400

    # Get data
    data = get_json(client.get(links['self'], headers=auth_headers), code=200)

    # Not allowed to delete
    assert client.delete(
        links['self'], headers=auth_headers).status_code == 403

    # Update metadata
    data = dict(metadata=data['metadata'])
    data['metadata'].update(dict(
        title='New title',
        access_right='closed',
        creators=[
            dict(name="Smith, Jane", affiliation="Atlantis"),
            dict(name="Doe, John", affiliation="Atlantis"),
        ],
        communities=[
            {'identifier': 'c1'}
        ]
    ))

    resdata = get_json(client.put(
        links['self'], data=json.dumps(data), headers=headers
    ), code=200)
    assert resdata['title'] == 'New title'
    assert resdata['metadata']['title'] == 'New title'

    # Try to change DOI
    data['metadata']['doi'] = '10.1234/foo'
    data = get_json(client.put(
        links['self'], data=json.dumps(data), headers=headers
    ), code=400)

    # Approve community
    c = Community.get('c1')
    _, record = resolver.resolve(str(record_id))
    c.accept_record(record)
    record.commit()
    db.session.commit()

    # Get record to confirm if both communities should be visible now
    assert get_json(client.get(
        url_for('invenio_records_rest.recid_item', pid_value=record_id),
        headers=json_headers,
    ), code=200)['metadata']['communities'] == [
        {'identifier': 'c1'},
        {'identifier': 'c3'},
    ]

    # Publish
    response = client.post(links['publish'], headers=auth_headers)
    data = get_json(response, code=202)
    current_search.flush_and_refresh(index='records')

    # - is record still accessible?
    postedit_data = get_json(client.get(
        url_for('invenio_records_rest.recid_item', pid_value=record_id),
        headers=json_headers,
    ), code=200)
    # - sanity checks
    assert postedit_data['doi'] == expected_doi
    assert postedit_data['record_id'] == record_id

    # - files should no longer be downloadable (closed access)
    # - download_url worked before edit, so make sure it doesn't work now.
    assert 'files' not in postedit_data
    assert client.get(download_url).status_code == 404

    # - c3 was removed, so only c1 one should be visible now
    assert postedit_data['metadata']['communities'] == [
        {'identifier': 'c1'},
    ]

    # Edit
    data = get_json(client.post(links['edit'], headers=auth_headers), code=201)

    # Update
    data = dict(metadata=data['metadata'])
    data['metadata'].update(dict(title='Will be discarded'))
    resdata = get_json(client.put(
        links['self'], data=json.dumps(data), headers=headers
    ), code=200)

    # Discard
    data = get_json(
        client.post(links['discard'], headers=auth_headers),
        code=201)

    # Get and assert metadata
    data = get_json(client.get(links['self'], headers=auth_headers), code=200)
    assert data['title'] == postedit_data['title']


def create_deposit(client, headers, auth_headers, deposit_url, get_json,
                   data):
    """Create a deposit via the API."""
    test_data = dict(
        metadata=dict(
            upload_type='software',
            title='Test title',
            creators=[
                dict(name='Doe, John', affiliation='Atlantis'),
            ],
            description='Test',
        )
    )
    test_data['metadata'].update(data)

    # Create deposit
    res = client.post(
        deposit_url, data=json.dumps(test_data), headers=headers)
    data = get_json(res, code=201)

    # Get identifier and links
    current_search.flush_and_refresh(index='deposits')
    links = data['links']

    # Upload file
    res = client.post(
        links['files'],
        data=dict(file=(BytesIO(b'ctx'), 'test.txt'), name='test.txt'),
        headers=auth_headers,
    )
    assert res.status_code == 201

    return links, data


def test_edit_doi(api_client, db, es, location, json_auth_headers,
                  deposit_url, get_json, auth_headers, json_headers,
                  license_record, communities, resolver):
    """Test editing of external DOI."""
    headers = json_auth_headers
    client = api_client

    data = dict(doi='10.1234/foo')
    links, data = create_deposit(
        client, headers, auth_headers, deposit_url, get_json, data)
    assert data['doi'] == '10.1234/foo'
    record_url = url_for(
        'invenio_records_rest.recid_item', pid_value=data['record_id'])

    # Create a persistent identifier
    PersistentIdentifier.create('doi', '10.1234/exists',
                                status=PIDStatus.REGISTERED)
    db.session.commit()

    # DOI exists
    data['metadata']['doi'] = '10.1234/exists'
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    assert res.status_code == 400

    # Update metadata
    data['metadata']['doi'] = '10.1234/bar'
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)
    assert data['doi'] == '10.1234/bar'

    # Publish
    res = client.post(links['publish'], headers=auth_headers)
    data = get_json(res, code=202)
    assert data['doi'] == '10.1234/bar'

    assert PersistentIdentifier.query.filter_by(pid_type='depid').count() == 1
    assert PersistentIdentifier.query.filter_by(pid_type='recid').count() == 1
    assert PersistentIdentifier.query.filter_by(pid_type='doi').count() == 2
    doi_exists = PersistentIdentifier.get(pid_type='doi',
                                          pid_value='10.1234/exists')
    doi_external = PersistentIdentifier.get(pid_type='doi',
                                            pid_value='10.1234/bar')
    assert doi_exists.status == PIDStatus.REGISTERED
    # User-provided DOIs are not registered
    assert doi_external.status == PIDStatus.RESERVED

    # Get record
    res = client.get(record_url, headers=json_headers)
    data = get_json(res, code=200)
    assert data['doi'] == '10.1234/bar'

    # Edit
    res = client.post(links['edit'], headers=auth_headers)
    data = get_json(res, code=201)
    assert data['doi'] == '10.1234/bar'

    # Update - cannot get a zenodo doi now.
    data['metadata']['doi'] = ''
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    assert res.status_code == 400

    # Update
    data['metadata']['doi'] = '10.4321/foo'
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)
    assert data['doi'] == '10.4321/foo'

    # Publish deposition
    res = client.post(links['publish'], headers=auth_headers)
    data = get_json(res, code=202)
    assert data['doi'] == '10.4321/foo'

    # Get record
    res = client.get(record_url, headers=json_headers)
    data = get_json(res, code=200)
    assert data['doi'] == '10.4321/foo'

    # Make sure the PIDs are correct
    assert PersistentIdentifier.query.filter_by(pid_type='depid').count() == 1
    assert PersistentIdentifier.query.filter_by(pid_type='recid').count() == 1
    assert PersistentIdentifier.query.filter_by(pid_type='doi').count() == 2
    doi_exists = PersistentIdentifier.get(pid_type='doi',
                                          pid_value='10.1234/exists')

    # external DOI should be updated
    doi_external = PersistentIdentifier.get(pid_type='doi',
                                            pid_value='10.4321/foo')
    assert doi_exists.status == PIDStatus.REGISTERED
    assert doi_external.status == PIDStatus.RESERVED


def test_noedit_doi(api_client, db, es, location, json_auth_headers,
                    deposit_url, get_json, auth_headers, json_headers,
                    license_record, communities, resolver):
    """Test editing of external DOI."""
    headers = json_auth_headers
    client = api_client

    links, data = create_deposit(
        client, headers, auth_headers, deposit_url, get_json, {})

    # Update metadata.
    data['metadata']['doi'] = '10.1234/bar'
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)

    # Update with pre-reserved DOI.
    prereserved = data['metadata']['prereserve_doi']['doi']
    data['metadata']['doi'] = prereserved
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)

    # Update with empty string.
    data['metadata']['doi'] = ''
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)

    # Publish
    res = client.post(links['publish'], headers=auth_headers)
    data = get_json(res, code=202)
    assert data['doi'] == prereserved

    # Edit
    res = client.post(links['edit'], headers=auth_headers)
    data = get_json(res, code=201)

    # Update with invalid DOIs
    for d in ['10.4321/foo', '']:
        data['metadata']['doi'] = d
        res = client.put(links['self'], data=json.dumps(data), headers=headers)
        res.status_code == 400

    # Update with only valid DOI.
    data['metadata']['doi'] = prereserved
    res = client.put(links['self'], data=json.dumps(data), headers=headers)
    data = get_json(res, code=200)

    # Publish deposition
    res = client.post(links['publish'], headers=auth_headers)
    data = get_json(res, code=202)

    # Check if PIDs have been created (depid, recid, doi)
    PersistentIdentifier.query.filter_by(pid_type='depid').one()
    PersistentIdentifier.query.filter_by(pid_type='recid').one()
    doi_pid = PersistentIdentifier.query.filter_by(pid_type='doi').one()
    assert doi_pid.status == PIDStatus.RESERVED


def test_publish_empty(api_client, db, es, location, json_auth_headers,
                       deposit_url, get_json, auth_headers, json_headers,
                       license_record, communities, resolver):
    """Test if it is possible to circumvent metadata validation."""
    headers = json_auth_headers
    client = api_client

    # Create deposit
    response = client.post(deposit_url, data='{}', headers=headers)
    data = get_json(response, code=201)

    # Get identifier and links
    current_search.flush_and_refresh(index='deposits')
    links = data['links']

    # Upload file
    res = client.post(
        links['files'],
        data=dict(file=(BytesIO(b'ctx'), 'test.txt'), name='test.txt'),
        headers=auth_headers,
    )
    assert res.status_code == 201

    # Publish deposition - not possible
    response = client.post(links['publish'], headers=auth_headers)
    data = get_json(response, code=400)


def test_delete_draft(api, api_client, db, es, location, json_auth_headers,
                      auth_headers, deposit_url, get_json, license_record):
    """Test deleting of Deposit draft using REST API."""
    # Setting var this way doesn't work
    headers = json_auth_headers
    client = api_client
    links, data = create_deposit(
        client, headers, auth_headers, deposit_url, get_json, {})

    recid = PersistentIdentifier.query.filter_by(pid_type='recid').one()
    depid = PersistentIdentifier.query.filter_by(pid_type='depid').one()
    assert recid.status == PIDStatus.RESERVED
    assert depid.status == PIDStatus.REGISTERED

    # Get deposition
    current_search.flush_and_refresh(index='deposits')
    response = client.get(links['self'], headers=auth_headers)
    assert response.status_code == 200

    # Delete deposition
    current_search.flush_and_refresh(index='deposits')
    response = client.delete(links['self'], headers=auth_headers)
    assert response.status_code == 204
    # 'recid' PID shuld be removed, while 'depid' should have status deleted.
    # No 'doi' PIDs should be created without publishing
    assert PersistentIdentifier.query.filter_by(pid_type='recid').count() == 0
    depid = PersistentIdentifier.query.filter_by(pid_type='depid').one()
    assert PersistentIdentifier.query.filter_by(pid_type='doi').count() == 0
    assert depid.status == PIDStatus.DELETED
