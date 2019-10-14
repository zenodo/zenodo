# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Test grant utilities."""

from __future__ import absolute_import, print_function

import os

from zenodo.modules.utils.grants import OpenAIREGrantsDump


def test_openaire_grants_dump(tmpdir, script_dir):
    """Test OpenAIRE grants dump parsing and splitting."""
    out_dir = tmpdir.mkdir('grants_db')
    out_dir_prefix = '{0}/grants-'.format(out_dir)
    grants_dump = OpenAIREGrantsDump(str(script_dir.join('grants-dump.gz')))
    split_files = list(grants_dump.split(out_dir_prefix, grants_per_file=2))
    assert split_files == [
        ('{}00.db'.format(out_dir_prefix), 2),
        ('{}01.db'.format(out_dir_prefix), 1),
    ]
    assert all(os.path.exists(filepath) for filepath, _ in split_files)
