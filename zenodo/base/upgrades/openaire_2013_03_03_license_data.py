# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

import warnings
from invenio.legacy.dbquery import run_sql
from invenio.utils.text import wait_for_user


depends_on = ['openaire_2013_02_18_zenodo_data']


def info():
    return "Install license data into knowledge base"


def do_upgrade():
    """ Install license data into knowledge base """
    import requests
    import json

    r = requests.get('http://licenses.opendefinition.org/licenses/groups/all.json')
    if r.status_code != 200:
        raise RuntimeError("Couldn't download http://licenses.opendefinition.org/licenses/groups/all.json")
    licenses = json.loads(r.text)

    res = run_sql("INSERT INTO knwKB (name,description,kbtype) VALUES ('licenses','','w')")
    for key, value in licenses.items():
        run_sql("INSERT INTO knwKBRVAL (m_key,m_value,id_knwKB) VALUES (%s,%s,%s)", (key, json.dumps(value), res))


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 5

def pre_upgrade():
    """  Run pre-upgrade checks (optional). """
    try:
        import requests
    except ImportError:
        raise RuntimeError("Python package requests not installed. Please install to continue.")
