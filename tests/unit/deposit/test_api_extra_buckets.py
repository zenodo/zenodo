# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
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

from __future__ import absolute_import, print_function, unicode_literals

from invenio_files_rest.models import Bucket

from zenodo.modules.deposit.resolvers import deposit_resolver
from zenodo.modules.records.resolvers import record_resolver

extra_formats_urls = {
    'deposit': '/deposit/depositions/{0}/formats',
    'record': '/records/{0}/formats'
}

extra_formats_headers = {
    'foo': [('Content-Type', 'application/foo+xml')],
    'bar': [('Content-Type', 'application/bar+xml')],
    'foo-accept': [('Accept', 'application/foo+xml')],
    'bar-accept': [('Accept', 'application/bar+xml')],
    'invalid-format': [('Content-Type', 'application/invalid-format+xml')],
}


def use_extra_formats_functions(
        extra_auth_headers, api_client, get_json, recid=None, depid=None):
    """Test all available actions on extra formats for deposit and record.

    After this function the extra formats bucket will contain a single file.
    """
    if depid:
        # Add extra_formats bucket with a file
        response = api_client.put(
            extra_formats_urls['deposit'].format(depid),
            data='foo file',
            headers=extra_formats_headers['foo'] + extra_auth_headers
        )
        data = get_json(response, code=200)
        assert data['message'] == 'Extra format "application/foo+xml" updated.'

        # Add file to extra_formats bucket
        response = api_client.put(
            extra_formats_urls['deposit'].format(depid),
            data='bar file content',
            headers=extra_formats_headers['bar'] + extra_auth_headers
        )
        data = get_json(response, code=200)
        assert data['message'] == 'Extra format "application/bar+xml" updated.'

        # Get the list of the extra_formats files attached to this deposit
        response = api_client.options(
            extra_formats_urls['deposit'].format(depid),
            headers=extra_auth_headers)
        data = get_json(response, code=200)

        assert {f['key'] for f in data} == \
            {'application/foo+xml', 'application/bar+xml'}

        if recid:
            response = api_client.options(
                extra_formats_urls['record'].format(recid))
            data = get_json(response, code=200)

            assert {f['key'] for f in data} == \
                {'application/foo+xml', 'application/bar+xml'}

            response = api_client.get(
                extra_formats_urls['record'].format(recid),
                headers=extra_formats_headers['foo-accept']
            )

            assert response.get_data(as_text=True) == 'foo file'

            response = api_client.get(
                extra_formats_urls['record'].format(recid),
                headers=extra_formats_headers['bar-accept']
            )

            assert response.get_data(as_text=True) == 'bar file content'

        # Delete a file from the extra_formats bucket
        response = api_client.delete(
            extra_formats_urls['deposit'].format(depid),
            headers=extra_formats_headers['bar'] + extra_auth_headers
        )
        data = get_json(response, code=200)
        assert data['message'] == 'Extra format "application/bar+xml" deleted.'

        # Get the list of the extra_formats files attached to this deposit
        response = api_client.options(
            extra_formats_urls['deposit'].format(depid),
            headers=extra_auth_headers)
        data = get_json(response, code=200)

        assert data[0]['key'] == 'application/foo+xml'
        assert len(data) == 1

        # Update the extra_formats file
        response = api_client.put(
            extra_formats_urls['deposit'].format(depid),
            data='foo file updated content',
            headers=extra_formats_headers['foo'] + extra_auth_headers
        )
        data = get_json(response, code=200)
        assert data['message'] == 'Extra format "application/foo+xml" updated.'

        # Check if the file is updated
        response = api_client.get(
            extra_formats_urls['deposit'].format(depid),
            headers=extra_formats_headers['foo-accept'] + extra_auth_headers
        )

        assert response.get_data(as_text=True) == 'foo file updated content'

        # Try to add a non-whitelisted extra format mimetype
        response = api_client.put(
            extra_formats_urls['deposit'].format(depid),
            data='A file that should not be accepted',
            headers=extra_formats_headers['invalid-format'] +
            extra_auth_headers
        )
        assert response.status_code == 400
        assert response.json['message'] == \
            '"application/invalid-format+xml" is not an acceptable MIMEType.'


def test_extra_formats_buckets(
        api, api_client, db, es, locations, json_extra_auth_headers,
        deposit_url, get_json, extra_auth_headers, json_headers,
        license_record, communities, resolver, minimal_deposit):
    """Test simple flow using REST API."""
    headers = json_extra_auth_headers
    client = api_client
    test_data = minimal_deposit

    # Create deposit
    response = client.post(
        deposit_url, json=test_data, headers=headers)
    data = get_json(response, code=201)
    # Get identifier and links
    depid = data['record_id']
    links = data['links']

    # Upload 1 files
    response = client.put(
        links['bucket'] + '/test1.txt',
        data='ctx',
        headers=extra_auth_headers,
    )
    assert response.status_code == 200

    # Check for extra_formats bucket
    response = api_client.options(
        extra_formats_urls['deposit'].format(depid), headers=headers)
    data = get_json(response, code=200)

    # Check that no extra_formats bucket is present
    buckets = Bucket.query.all()
    assert len(buckets) == 1

    # There are no extra_formats files
    assert data == []

    use_extra_formats_functions(
        extra_auth_headers, api_client, get_json, depid=depid)

    buckets = Bucket.query.all()
    assert len(buckets) == 2

    deposit = deposit_resolver.resolve(depid)[1]
    assert deposit['_buckets']['extra_formats'] == \
        str(deposit.extra_formats.bucket.id)
    # Publish deposition
    response = client.post(links['publish'], headers=extra_auth_headers)
    data = get_json(response, code=202)
    first_version_recid = data['record_id']

    # Get the list of the extra_formats files attached to this deposit
    response = api_client.options(
        extra_formats_urls['record'].format(first_version_recid))
    data = get_json(response, code=200)

    assert data[0]['key'] == 'application/foo+xml'
    assert len(data) == 1

    # Test actions and clear extra_formats bucket
    use_extra_formats_functions(extra_auth_headers, api_client, get_json,
                                depid=depid, recid=first_version_recid)

    # Get newversion url
    data = get_json(
        client.get(links['self'], headers=extra_auth_headers), code=200
        )
    new_version_url = data['links']['newversion']

    # New Version
    data = get_json(
        client.post(new_version_url, headers=extra_auth_headers), code=201)
    links = data['links']

    # Get the list of the extra_formats files attached to the new deposit
    # Should be the same with the previous version
    response = api_client.options(
        extra_formats_urls['deposit'].format(depid),
        headers=extra_auth_headers
        )
    data = get_json(response, code=200)

    assert data[0]['key'] == 'application/foo+xml'
    assert len(data) == 1

    # Get latest version
    data = get_json(
        client.get(links['latest_draft'], headers=extra_auth_headers),
        code=200)
    links = data['links']
    depid = data['record_id']

    # Add a file to the new deposit
    get_json(client.put(
        links['bucket'] + '/newfile.txt',
        data='newfile',
        headers=extra_auth_headers,
    ), code=200)

    # Publish the new record
    response = client.post(links['publish'], headers=extra_auth_headers)
    data = get_json(response, code=202)
    links = data['links']
    recid = data['record_id']

    # Get the list of the extra_formats files attached to the new record
    response = api_client.options(extra_formats_urls['record'].format(recid))
    data = get_json(response, code=200)

    assert data[0]['key'] == 'application/foo+xml'
    assert len(data) == 1

    # Add file to extra_formats bucket
    response = api_client.put(
        extra_formats_urls['deposit'].format(recid),
        data='bar file content',
        headers=extra_formats_headers['bar'] + extra_auth_headers
    )
    data = get_json(response, code=200)
    assert data['message'] == 'Extra format "application/bar+xml" updated.'

    # Get the list of the extra_formats files attached to the new record
    response = api_client.options(extra_formats_urls['record'].format(recid))
    data = get_json(response, code=200)

    assert {f['key'] for f in data} == \
        {'application/foo+xml', 'application/bar+xml'}

    # Get the list of the extra_formats files attached to the previous record
    # Make sure that the snapshots are independent
    response = api_client.options(
        extra_formats_urls['record'].format(first_version_recid))
    data = get_json(response, code=200)

    first_record = record_resolver.resolve(first_version_recid)[1]
    new_record = record_resolver.resolve(recid)[1]
    assert first_record.extra_formats.bucket.id != \
        new_record.extra_formats.bucket.id

    assert data[0]['key'] == 'application/foo+xml'
    assert len(data) == 1

    # Test actions and clear extra_formats bucket of deposit
    use_extra_formats_functions(
        extra_auth_headers, api_client, get_json, depid=depid, recid=recid)


def test_delete_deposit_with_extra_formats_bucket(
        api, api_client, db, es, locations, json_extra_auth_headers,
        deposit_url, get_json, extra_auth_headers, license_record,
        communities, resolver, minimal_deposit):
    """Test deleting a deposit with extra formats."""
    headers = json_extra_auth_headers
    client = api_client
    test_data = minimal_deposit

    # Create deposit
    response = client.post(
        deposit_url, json=test_data, headers=headers)
    data = get_json(response, code=201)
    depid = data['record_id']

    # Get identifier and links
    links = data['links']

    # Add extra_formats bucket with a file
    response = api_client.put(
        extra_formats_urls['deposit'].format(depid),
        data='foo file',
        headers=extra_formats_headers['foo'] + extra_auth_headers
    )
    data = get_json(response, code=200)
    assert data['message'] == 'Extra format "application/foo+xml" updated.'

    # Delete Deposit
    response = client.delete(links['self'], headers=extra_auth_headers)
    assert response.status_code == 204

    # Buckets for files and extra_formats are cleaned.
    buckets = Bucket.query.all()
    assert len(buckets) == 0


def test_add_extra_formats_bucket_to_published_record(
        api, api_client, db, es, locations, json_extra_auth_headers,
        deposit_url, get_json, extra_auth_headers, license_record,
        communities, resolver, minimal_deposit):
    """Test adding extra formats to an already published record."""
    headers = json_extra_auth_headers
    client = api_client
    test_data = minimal_deposit

    # Create deposit
    response = client.post(
        deposit_url, json=test_data, headers=headers)
    data = get_json(response, code=201)
    depid = data['record_id']

    # Get identifier and links
    links = data['links']

    # Upload 1 files
    response = client.put(
        links['bucket'] + '/test1.txt',
        data='ctx',
        headers=extra_auth_headers,
    )
    assert response.status_code == 200

    # Publish deposition
    response = client.post(links['publish'], headers=extra_auth_headers)
    data = get_json(response, code=202)
    recid = data['record_id']

    # Add extra_formats bucket with a file
    response = api_client.put(
        extra_formats_urls['deposit'].format(recid),
        data='foo file',
        headers=extra_formats_headers['foo'] + extra_auth_headers
    )
    data = get_json(response, code=200)
    assert data['message'] == 'Extra format "application/foo+xml" updated.'

    response = api_client.options(extra_formats_urls['record'].format(recid))
    data = get_json(response, code=200)

    assert data[0]['key'] == 'application/foo+xml'
    assert len(data) == 1
    use_extra_formats_functions(
        extra_auth_headers, api_client, get_json, depid=depid, recid=recid)
