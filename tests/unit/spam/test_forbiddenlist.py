# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2022 CERN.
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

"""Test forbidden list."""

import os
import pytest
import tempfile

from zenodo.modules.spam.forbiddenlist import DomainForbiddenList


@pytest.yield_fixture(scope='session')
def tmp_spam_domains_file():
    """Temporary spam domains file path."""
    fp = tempfile.NamedTemporaryFile(mode="wb")
    fp.write(b"testing.com\n")
    fp.write(b"some.other.ch\n")
    fp.flush()
    yield fp.name
    fp.close()


def test_forbidden_list_search(tmp_spam_domains_file):
    fl = DomainForbiddenList(tmp_spam_domains_file)

    assert not fl.is_forbidden("test.com")
    assert not fl.is_forbidden("other.ch")
    assert fl.is_forbidden("testing.com")
    assert fl.is_forbidden("some.other.ch")
