from __future__ import absolute_import

import json
from functools import partial
from flask import url_for
from invenio.ext.sqlalchemy import db
from invenio.ext.restful.utils import APITestCase
from invenio.base.globals import cfg
from invenio.testsuite import make_pdf_fixture


def tclient_request_factory(client, method, endpoint, urlargs, data,
                            is_json, headers, files, verify_ssl):
    """
    Make requests with test client package
    """
    client_func = getattr(client, method.lower())

    if headers is None:
        headers = [('Content-Type', 'application/json')] if is_json else []

    if data is not None:
        request_args = dict(
            data=json.dumps(data) if is_json else data,
            headers=headers,
        )
    else:
        request_args = {}

    if files is not None:
        data.update({
            'file': (files['file'], data['filename']),
            'name': data['filename']
        })
        del data['filename']

    resp = client_func(
        url_for(
            endpoint,
            _external=False,
            **urlargs
        ),
        base_url=cfg['CFG_SITE_SECURE_URL'],
        **request_args
    )

    # Patch response
    resp.json = lambda: json.loads(resp.data)
    return resp


class ZenodoUploadTestCase(APITestCase):
    def setUp(self):
        from invenio.modules.accounts.models import User
        self.user = User(
            email='info@invenio-software.org', nickname='tester'
        )
        self.user.password = "tester"
        db.session.add(self.user)
        db.session.commit()
        self.create_oauth_token(
            self.user.id, scopes=["deposit:write", "deposit:actions"]
        )

    def tearDown(self):
        self.remove_oauth_token()
        if self.user:
            db.session.delete(self.user)
            db.session.commit()

    def test_upload(self):
        from ..upload import upload

        # Make request with test client instead of requests library
        factory = partial(tclient_request_factory, self.client)

        metadata = dict(
            upload_type="software",
            title="Test title",
            creators=[
                dict(name="Doe, John", affiliation="Atlantis"),
                dict(name="Smith, Jane", affiliation="Atlantis")
            ],
            description="Test Description",
            publication_date="2013-05-08",
        )
        files = [make_pdf_fixture('test.pdf', "upload test")]

        metadata = upload(
            self.accesstoken,
            metadata,
            files,
            publish=True,
            request_factory=factory
        )
        assert 'record_id' in metadata
        assert 'doi' in metadata
