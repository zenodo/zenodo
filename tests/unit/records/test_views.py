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

from datetime import date, timedelta
from flask import render_template_string


def test_is_valid_access_right(app):
    """Test template test."""
    assert render_template_string("{{ 'open' is accessright }}") == "True"
    assert render_template_string("{{ 'invalid' is accessright }}") == "False"


def test_is_embargoed(app):
    """Test template test."""
    assert render_template_string(
        "{{ dt is embargoed }}", dt=date.today()) == "False"
    assert render_template_string(
        "{{ dt is embargoed }}", dt=date.today()+timedelta(days=1)) == "True"
    assert render_template_string(
        "{{ dt is embargoed(accessright='open') }}",
        dt=date.today()+timedelta(days=1)) == "False"
    assert render_template_string(
        "{{ dt is embargoed(accessright='embargoed') }}",
        dt=date.today()+timedelta(days=1)) == "True"
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
    app.config['ZENODO_LOCAL_DOI_PREFIXES'] = ['10.123', '10.5281']
    assert render_template_string(
        "{{ '10.123/foo' is local_doi }}") == "True"
    assert render_template_string(
        "{{ '10.1234/foo' is local_doi }}") == "False"
    assert render_template_string(
        "{{ '10.5281/foo' is local_doi }}") == "True"


def test_relation_title(app):
    """Test relation title."""
    assert render_template_string(
        "{{ 'isCitedBy'|relation_title }}") == "Cited by"
    assert render_template_string(
        "{{ 'isIdenticalTo'|relation_title }}") == "isIdenticalTo"


def test_pid_url(app):
    """Test pid_url."""
    assert render_template_string(
        "{{ '10.123/foo'|pid_url }}") == "http://dx.doi.org/10.123/foo"
    assert render_template_string(
        "{{ 'asfasdf'|pid_url }}") == ""
    assert render_template_string(
        "{{ 'arXiv:1512.01558'|pid_url(scheme='arxiv') }}") \
        == "http://arxiv.org/abs/arXiv:1512.01558"
