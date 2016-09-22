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

"""Zenodo fixtures CLI test cases."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner
from invenio_pages.models import Page

from zenodo.modules.fixtures.cli import loadpages_cli


def test_loadpages(script_info, db):
    """Test version import."""
    assert Page.query.count() == 0
    runner = CliRunner()
    res = runner.invoke(loadpages_cli, [], obj=script_info)
    assert res.exit_code == 0
    assert Page.query.count() == 10
    page = Page.query.filter_by(url='/about').one()
    assert page.title == 'About Zenodo'
    assert len(page.description) > 20
    assert len(page.content) > 100
    assert page.template_name == 'invenio_pages/dynamic.html'
    res = runner.invoke(loadpages_cli, [], obj=script_info)
    assert res.exit_code != 0
    res = runner.invoke(loadpages_cli, ['-f'], obj=script_info)
    assert res.exit_code == 0

    for p in Page.query.all():
        assert p.title
        assert p.url
        assert p.template_name
