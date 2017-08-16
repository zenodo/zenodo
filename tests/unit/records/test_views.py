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

"""Zenodo records views."""

from __future__ import absolute_import, print_function

import json
from datetime import datetime, timedelta

from flask import render_template_string, url_for
from helpers import login_user_via_session
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record
from invenio_search import current_search

from zenodo.modules.records.views import zenodo_related_links


def test_is_valid_access_right(app):
    """Test template test."""
    assert render_template_string("{{ 'open' is accessright }}") == "True"
    assert render_template_string("{{ 'invalid' is accessright }}") == "False"


def test_is_embargoed(app):
    """Test template test."""
    today = datetime.utcnow().date()
    assert render_template_string(
        "{{ dt is embargoed }}", dt=today) == "False"
    assert render_template_string(
        "{{ dt is embargoed }}", dt=today+timedelta(days=1)) == "True"
    assert render_template_string(
        "{{ dt is embargoed(accessright='open') }}",
        dt=today+timedelta(days=1)) == "False"
    assert render_template_string(
        "{{ dt is embargoed(accessright='embargoed') }}",
        dt=today+timedelta(days=1)) == "True"
    assert render_template_string(
        "{{ dt is embargoed(accessright='embargoed') }}",
        dt=None) == "False"


def test_accessright_category(app):
    """Test template filter."""
    assert render_template_string(
        "{{ 'open'|accessright_category }}") == "success"


def test_accessright_title(app):
    """Test template filter."""
    assert render_template_string(
        "{{ 'open'|accessright_title }}") == "Open Access"


def test_objecttype(app):
    """Test template filter."""
    assert render_template_string(
        r"{% set t = upload_type|objecttype %}{{ t.title.en }}",
        upload_type=dict(type="publication", subtype="book")) == "Book"

    assert render_template_string(
        r"{% set t = upload_type|objecttype %}{{ t.title.en }}",
        upload_type=dict(type="publication")) == "Publication"

    assert render_template_string(
        r"{% set t = upload_type|objecttype %}{{ t }}",
        upload_type="") == "None"


def test_local_doi(app):
    """Test template test."""
    orig = app.config['ZENODO_LOCAL_DOI_PREFIXES']
    app.config['ZENODO_LOCAL_DOI_PREFIXES'] = ['10.123', '10.5281']
    assert render_template_string(
        "{{ '10.123/foo' is local_doi }}") == "True"
    assert render_template_string(
        "{{ '10.1234/foo' is local_doi }}") == "False"
    assert render_template_string(
        "{{ '10.5281/foo' is local_doi }}") == "True"

    app.config['ZENODO_LOCAL_DOI_PREFIXES'] = orig


def test_relation_title(app):
    """Test relation title."""
    assert render_template_string(
        "{{ 'isCitedBy'|relation_title }}") == "Cited by"
    assert render_template_string(
        "{{ 'nonExistingRelation'|relation_title }}") == "nonExistingRelation"


def test_relation_logo(app):
    """Test relation logo."""
    no_relations = {}
    assert zenodo_related_links(no_relations, []) == []

    class MockCommunity(object):
        id = 'zenodo'

    github_relation = {
        'communities': [
            'zenodo',
        ],
        'related_identifiers': [
            {
                'scheme': 'url',
                'relation': 'isSupplementTo',
                'identifier': 'https://github.com/'
                              'TaghiAliyev/BBiCat/tree/v1.0.4-alpha',
            }
        ],
    }
    assert zenodo_related_links(github_relation, [MockCommunity]) == [
        {
            'image': 'img/github.png',
            'link': 'https://github.com/TaghiAliyev/BBiCat/tree/v1.0.4-alpha',
            'prefix': 'https://github.com',
            'relation': 'isSupplementTo',
            'scheme': 'url',
            'text': 'Available in'
        }
    ]


def test_pid_url(app):
    """Test pid_url."""
    assert render_template_string(
        "{{ '10.123/foo'|pid_url }}") == "https://doi.org/10.123/foo"
    assert render_template_string(
        "{{ 'doi: 10.123/foo'|pid_url(scheme='doi') }}") \
        == "https://doi.org/10.123/foo"
    assert render_template_string(
        "{{ 'asfasdf'|pid_url }}") == ""
    assert render_template_string(
        "{{ 'arXiv:1512.01558'|pid_url(scheme='arxiv', url_scheme='http') }}"
    ) == "http://arxiv.org/abs/arXiv:1512.01558"
    assert render_template_string(
        "{{ 'arXiv:1512.01558'|pid_url(scheme='arxiv') }}") \
        == "https://arxiv.org/abs/arXiv:1512.01558"
    assert render_template_string(
        "{{ 'hdl.handle.net/1234/5678'|pid_url(scheme='handle') }}") \
        == "https://hdl.handle.net/1234/5678"


def test_records_ui_export(app, db, full_record):
    """Test export pages."""
    r = Record.create(full_record)
    PersistentIdentifier.create(
        'recid', '12345', object_type='rec', object_uuid=r.id,
        status=PIDStatus.REGISTERED)
    db.session.commit()

    formats = app.config['ZENODO_RECORDS_EXPORTFORMATS']
    with app.test_client() as client:
        for f, val in formats.items():
            res = client.get(url_for(
                'invenio_records_ui.recid_export', pid_value='12345',
                format=f))
            assert res.status_code == 410 if val is None else 200


def test_citation_formatter_styles_get(api, api_client, db):
    """Test get CSL styles."""
    with api.test_request_context():
        style_url = url_for('invenio_csl_rest.styles')
    res = api_client.get(style_url)
    styles = json.loads(res.get_data(as_text=True))
    assert res.status_code == 200
    assert 'apa' in styles
    assert 'American Psychological Association' in styles['apa']


def test_citation_formatter_citeproc_get(api, api_client, es, db, full_record,
                                         users):
    """Test records REST citeproc get."""
    r = Record.create(full_record)
    pid = PersistentIdentifier.create(
        'recid', '12345', object_type='rec', object_uuid=r.id,
        status=PIDStatus.REGISTERED)
    db.session.commit()
    db.session.refresh(pid)

    RecordIndexer().index_by_id(r.id)
    current_search.flush_and_refresh(index='records')
    login_user_via_session(api_client, email=users[2]['email'])

    with api.test_request_context():
        records_url = url_for('invenio_records_rest.recid_item',
                              pid_value=pid.pid_value)

    res = api_client.get(records_url,
                         query_string={'style': 'apa'},
                         headers={'Accept': 'text/x-bibliography'})
    assert res.status_code == 200
    assert 'Doe, J.' in res.get_data(as_text=True)
    assert 'Test title.' in res.get_data(as_text=True)
    assert '(2014).' in res.get_data(as_text=True)
