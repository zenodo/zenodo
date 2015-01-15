# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Standardise on Zenodo collection names."""

from invenio.legacy.dbquery import run_sql


depends_on = [u'zenodo_2014_11_25_workflowobjectfix']


def info():
    return "Standardise on Zenodo collection names."


def do_upgrade():
    run_sql("UPDATE collection SET name='Zenodo' WHERE name='ZENODO'")
    run_sql("UPDATE collectionname SET value='Zenodo' WHERE value='ZENODO'")
    run_sql("UPDATE collectionname SET value='Provisional: Zenodo' "
            "WHERE value='Provisional: ZENODO'")
    run_sql("UPDATE accARGUMENT SET value='Zenodo' WHERE value='ZENODO'")
    run_sql("UPDATE community SET title='Zenodo' WHERE id='zenodo'")


def estimate():
    return 1
